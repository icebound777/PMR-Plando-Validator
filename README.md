# Plandomizer for the Open World Paper Mario Randomizer

This tool is to be used with the Open World Paper Mario Randomizer, and allows setting certain parameters, like guaranteed item placement, costs of moves, and more.

This tool is imported into the randomizer as a submodule, but it can be used as a standalone tool for validating a plando file in JSON format.

Randomizer main repository: <https://github.com/icebound777/PMR-SeedGenerator>

## How to use

### How to use (as player)

Copy the provided `plando_blank.json` file, edit its contents to whatever values you wish to guarantee in the randomizer, then pass the file to the randomizer.

For pointers on how to edit the file properly, see the `Layout and allowed data of the plando file` section further below.

### How to use (as a developer)

Take the plando file provided by the player and pass its contents to the provided `plando_validator.py` module. Either pass a file path to the plando file to the `validate_from_filepath()` function, or run the file's contents through a JSON parser beforehand and then pass the data as dict to the `validate_from_dict()` function. The validator module then checks the data layout, and runs sanity checks on its contents.

The validator module then returns two dictionaries:

* a data dictionary that's either:
  * the checked and converted data, if there were no errors, or
  * an empty dict, if there were one or more errors
* a messages dictionary, which always has two keys:
  * a `"warnings"` key, which holds a list of strings of warnings. These don't cause the data dictionary being empty
  * an `"errors"` key, which holds a list of strings of errors. These do cause the data dictionary being empty

Warnings *can* be ignored, but may or may not cause weirdness or issues in the game later on.

Errors mean that there is something so wrong with the data provided that seed generation failure is likely, if not guaranteed.

The returned data can then be handed to the seed generator.

## Layout and allowed data of the plando file

At the top level, the following fields are allowed:

* `"difficulty"`
* `"boss_battles"`
* `"required_spirits"`
* `"move_costs"`
* `"item_placement"`

Every other top level field gets ignored during parsing, and gets logged as a warning.

Any of these fields that are not provided will simply not be modified by the plando file. E.g. if you do not want to manually set the chapter difficulties, you may remove the `"difficulty"` section entirely.

Providing invalid values to any of these fields causes errors.

### Difficulty

Type: key-value-pairs
Schema: `"chapter X": Y`
Values:

* `X`: chapter to set the difficulty for. Allowed range: `1-7`
* `Y`: difficulty to set. Allowed values: `1-8, null`

Example: `"chapter 1": 5, chapter 2: 2, chapter 4: null`
Notes:

* Setting the difficulty for chapter 8 is currently not possible
* Setting a chapter difficulty to `null`, or excluding a given chapter entirely, results in the seed generator setting the difficulty itself according to given settings
* Will cause a warning if the difficulties of chapters 1, 2 or 5 are manually set to a value above 3, as these are available starting locations a player may find difficult to deal with when scaled too highly
* The difficulty section gets ignored if the `Progressive Scaling` option is active

### Boss Battles

Type: key-value-pairs
Schema: `"chapter X": "Y"`
Values:

* `X`: chapter to set the boss battle for. Allowed range: `1-7`
* `Y`: boss battle to set. Allowed values:
  * `KoopaBros`
  * `Tutankoopa`
  * `TubbasHeart`
  * `GeneralGuy`
  * `LavaPiranha`
  * `HuffNPuff`
  * `CrystalKing`
  * `null`

Example: `"chapter 1": "Tutankoopa", chapter 2: "HuffNPuff", chapter 4: null`
Notes:

* Setting a chapter's boss to `null`, or excluding a given chapter entirely, results in the seed generator setting the boss battle itself according to given settings
* Placing any boss at all will cause a warning, unless you set all bosses and use each boss exactly once. This is due to the possibility of having a boss appear multiple times in the same seed, which is dependent on the settings. This should work just fine during `Progressive Scaling`, but may behave weirdly with any other difficulty setting

### Required Spirits

Type: list
Schema: `"X"` (string) or `X` (number)
Values:

* `"X"`: name of star spirit. Allowed values: `"Eldstar", "Mamar", "Skolar", "Muskular", "Misstar", "Klevar", "Kalmar"`
* alternatively: `X`: number of chapter. Allowed range: `1-7`

Examples: `"Mamar", "Muskular", "Kalmar"`, `2, 4, 7`, `"Mamar", "Muskular", 7`
Notes:

* The required spirits get ignored if the seed settings don't set `Require Specific Spirits`, or if all 7 spirits are set as required
* Will always cause a warning, as having `Require Specific Spirits` active and setting more spirits here than are required to open Star Way will have the spirits set here overwrite the number of spirits required for Star Way
* Will cause a warning if all 7 spirits are set as required
* Will cause a warning if the same spirit is set multiple times

### Move Costs

The `"move_costs"` field can hold the following three dictionaries:

* `"badge"`

The `"badge"` dictionary holds the badge names (string) as keys and their move costs as a dictionary of cost type (string) (either "BP", "FP", or both, depending on the badge) to cost (number). The BP costs have a range of 0-10, the FP costs a range of 0-75.

* `"partner"`

The `"partner"` dictionary holds the partners (string) as keys and their move costs as a dictionary of movename (string) to FP cost (number). The costs have a range of 0-75.

* `"starpower"`

The `"starpower"` dictionary holds the starpower moves (string) as keys and their SP costs as values (number). The costs have a range of 0-7.

For the allowed keys, refer to the `plando_blank.json` defaults file.

Any cost field not set, or set to `null`, will adhere to vanilla values or get randomized, depending on chosen settings.

### Item Placement

The `"items"` field can hold keys for the different areas in the game (str), which each have a dictionary of their item locations (str) to the placed items (str). In the case of shop item locations the placed items will itself be a dictionary instead, holding its item (str) and its sell price for that item (int). Any area or item location within that area not set, or set to `null`, will adhere to the chosen randomizer settings.

For the available areas and item locations, refer to the `plando_blank.json` defaults file.

Item placement has the following rules:

* Unique items
  * Generally, unique items may only be placed once, except for certain keys and badges
  * Placing more than the allowed number of instances of a given unique items will cause an error
* Partners
  * Any partners not manually set will be placed according to seed settings
* Progression Key items
  * All key items may only be placed once, except for
    * KoopaFortressKey (up to 4)
    * RuinsKey (up to 4)
    * TubbaCastleKey (up to 3)
    * BowserCastleKey (up to 5)
    * PrisonKey (up to 2)
* Partner Upgrades
  * Each Partner Upgrade may be placed up to two times
  * Placing any partner upgrade will forcibly turn on `Partner Upgrade Shuffle` if it is turned off, and cause a warning
* Progressive Gear Upgrades
  * Each Progressive Gear Upgrade may be placed up to three times
* Badges
  * All badges may only be placed once, except for
    * PowerPlus (up to 3)
    * HPPlus (up to 5)
    * FPPlus (up to 5)
    * DeepFocus (up to 3)
    * DamageDodge (up to 3)
    * DefendPlus (up to 3)
    * HappyHeart (up to 3)
    * HappyFlower (up to 3)
    * FlowerSaver (up to 3)
  * Manually placed badges will count against the `Badge Pool Limit` setting, but won't be removed if said limit is lower than the number of manually placed badges
  * Manually placing any badges that would be removed by turning on the `Progressive Badges` setting will cause a warning and forcibly turn off `Progressive Badges`
  * Manually placing any progressive badges will cause a warning and forcibly turn on `Progressive Badges`
  * Manually placing both progressive badges and non-progressive badges of the same "badge family" will cause an error
* Star Pieces
  * At most 82 star pieces may be placed
  * Placing more than 34 star pieces will result in a warning, as that many star pieces can usually be found on the overworld. All other placeable star pieces are obtained via hidden panels or delivering letters.
  * It should generally be fine to place ...
    * up to 34 star pieces if neither hidden panels nor letter rewards are shuffled,
    * up to 45 star pieces if letter rewards are shuffled, but not hidden panels,
    * up to 70 star pieces if hidden panels are shuffled, but not letter rewards,
    * up to 81 star pieces otherwise
  * At most 5 Three Star Pieces items may be placed. Placing any of these will result in a warning, as these are usually obtained via Koopa Koot
  * If you place more star pieces than the settings chosen support, star pieces will be removed from non-randomized star piece locations to compensate. So it might happen that some hidden panels hold a consumable instead of a star piece, even though the hidden panels are not shuffled
* Power Stars
  * At most 120 power stars may be placed
  * If too few are placed to reach the value set for the `Total Power Stars` setting, then additional power stars will be placed by the randomizer
  * If more than `Total Power Stars` are placed manually, then the value for that setting will be increased to the number of stars actually placed
  * Power stars may be placed even if no setting requires collecting them
* Item Traps
  * Traps may be placed by using the item name `"TRAP"`. This will pick a random unique item sprite to represent the trap
  * Trap items may be appended by an item name in parentheses, to force the trap to take that item's sprite. For example: `"TRAP (UltraStone)"`. This allows arbitrary item trap sprites, even those are usually not chosen by the randomizer, like consumables. Coins, however, cannot be used as trap items
  * Traps may not be placed into item shops, Rowf's shop or Merlow's star piece trade
  * Manually placed traps count against the number of traps to be placed according to the `Item Trap Mode` setting, but won't be removed if that setting is lower than the number of manually placed traps
* Item shop prices
  * Prices in shops selling items for coins can be set from 0-999
  * Prices in Merlow's star piece shop cannot be adjusted, and if changed anyway will cause a warning and be ignored
* Super Block and Multi Coin Block locations
  * Are currently always ignored. Will cause a warning if set

The following values may be set as placed items:

* Special values
  * `TRAP`: Place a random trap
  * `TRAP (itemname)`: Place a trap with `itemname` as its sprite
  * `NonProgression`: Places a random consumable or non-progression unique item (key/partnerupgrade/badge)
  * `Consumable`: Places a random consumable
* Unique items
  * Key Items
    * `UltraStone`
    * `Dolly`
    * `StoreroomKey`
    * `FryingPan`
    * `Dictionary`
    * `Cookbook`
    * `Calculator`
    * `Mailbag`
    * `Melody`
    * `OddKey`
    * `KooperShell`
    * `KoopaFortressKey` (up to 4)
    * `Lyrics`
    * `PulseStone`
    * `RuinsKey` (up to 4)
    * `LunarStone`
    * `PyramidStone`
    * `DiamondStone`
    * `Artifact`
    * `ForestPass`
    * `BooRecord`
    * `BooWeight`
    * `BooPortrait`
    * `TubbaCastleKey` (up to 3)
    * `ToyTrain`
    * `MysteryNote`
    * `JadeRaven`
    * `VolcanoVase`
    * `MagicalSeed1`
    * `MagicalSeed2`
    * `MagicalSeed3`
    * `MagicalSeed4`
    * `WaterStone`
    * `MagicalBean`
    * `FertileSoil`
    * `MiracleWater`
    * `CrystalBerry`
    * `WarehouseKey`
    * `SnowmanScarf`
    * `SnowmanBucket`
    * `StarStone`
    * `BlueKey`
    * `RedKey`
    * `CrystalPalaceKey`
    * `BowserCastleKey` (up to 5)
    * `PrisonKey` (up to 2)
    * `KootKoopaLegends`
    * `KootTheTape`
    * `KootLuigiAutograph`
    * `KootEmptyWallet`
    * `CrystalBall`
    * `KootMerluvleeAutograph`
    * `KootOldPhoto`
    * `KootGlasses`
    * `KootPackage`
    * `KootRedJar`
    * `SilverCredit`
    * `GoldCredit`
    * `FirstDegreeCard`
    * `SecondDegreeCard`
    * `ThirdDegreeCard`
    * `FourthDegreeCard`
    * `Diploma`
    * `Letter (To Nomadimouse)`
    * `Letter (To Merlon)`
    * `Letter (To Little Mouser)`
    * `Letter (To Merlow)`
    * `Letter (To Fishmael)`
    * `Letter (To Miss T.)`
    * `Letter (To Frost T.)`
    * `Letter (To Goompa)`
    * `Letter (To Dane T.) 1`
    * `Letter (To Dane T.) 2`
    * `Letter (To Mr. E.)`
    * `Letter (To Igor)`
    * `Letter (To Franky)`
    * `Letter (To Muss T.)`
    * `Letter (To Minh T.)`
    * `Letter (To Russ T.)`
    * `Letter (To Goompapa) 1`
    * `Letter (To Goompapa) 2`
    * `Letter (To Koover) 1`
    * `Letter (To Koover) 2`
    * `Letter (To Mayor Penguin)`
    * `Letter (To Kolorado)`
    * `Letter (To Red Yoshi Kid)`
    * `Letter (To Mort T.)`
    * `Letter (To Fice T.)`
  * Badges
    * `PowerPlus` (up to 3)
    * `AllorNothing`
    * `PowerRush`
    * `MegaRush`
    * `PUpDDown`
    * `PDownDUp`
    * `IcePower`
    * `Berserker`
    * `RightOn`
    * `SpikeShield`
    * `FireShield`
    * `ZapTap`
    * `LastStand`
    * `DamageDodge` (up to 3)
    * `DefendPlus` (up to 3)
    * `DodgeMaster`
    * `CloseCall`
    * `PrettyLucky`
    * `LuckyDay`
    * `HealthyHealthy`
    * `FeelingFine`
    * `HPPlus` (up to 5)
    * `FPPlus` (up to 5)
    * `HappyHeart` (up to 3)
    * `CrazyHeart`
    * `HappyFlower` (up to 3)
    * `FlowerSaver` (up to 3)
    * `FlowerFanatic`
    * `HeartFinder`
    * `FlowerFinder`
    * `DoubleDip`
    * `TripleDip`
    * `Refund`
    * `QuickChange`
    * `ChillOut`
    * `DizzyAttack`
    * `FirstAttack`
    * `SpinAttack`
    * `BumpAttack`
    * `HPDrain`
    * `MegaHPDrain`
    * `PayOff`
    * `MoneyMoney`
    * `RunawayPay`
    * `ISpy`
    * `SpeedySpin`
    * `Peekaboo`
    * `DeepFocus` (up to 3)
    * `SuperFocus`
    * `GroupFocus`
    * `AttackFXA`
    * `AttackFXB`
    * `AttackFXC`
    * `AttackFXD`
    * `AttackFXE`
    * `AttackFXF`
    * `SlowGo`
    * `Multibounce`
    * `AutoMultibounce`
    * `PowerBounce`
    * `SleepStomp`
    * `DizzyStomp`
    * `MiniJumpCharge`
    * `JumpCharge`
    * `SJumpCharge`
    * `ProgressiveJumpCharge` (up to 3)
    * `AutoJump`
    * `PowerJump`
    * `SuperJump`
    * `MegaJump`
    * `ProgressivePowerJump` (up to 3)
    * `DDownJump`
    * `ShrinkStomp`
    * `QuakeBounce`
    * `SpinSmash`
    * `QuakeHammer`
    * `PowerQuake`
    * `MegaQuake`
    * `ProgressiveQuakeHammer` (up to 3)
    * `DDownPound`
    * `MiniSmashCharge`
    * `SmashCharge`
    * `SSmashChg`
    * `ProgressiveSmashCharge` (up to 3)
    * `HammerThrow`
    * `AutoSmash`
    * `PowerSmash`
    * `SuperSmash`
    * `MegaSmash`
    * `ProgressivePowerSmash` (up to 3)
    * `ShrinkSmash`
  * Gear (up to 3 each)
    * `ProgressiveHammer`
    * `ProgressiveBoots`
  * Partners
    * `Goombario`
    * `Kooper`
    * `Bombette`
    * `Parakarry`
    * `Bow`
    * `Watt`
    * `Sushie`
    * `Lakilester`
  * Partner Upgrades (up to 2 each)
    * `GoombarioUpgrade`
    * `KooperUpgrade`
    * `BombetteUpgrade`
    * `ParakarryUpgrade`
    * `BowUpgrade`
    * `WattUpgrade`
    * `SushieUpgrade`
    * `LakilesterUpgrade`
  * Star Powers
    * `StarBeam`
  * `ItemPouch` (up to 5)
* Collectables
  * `Coin`
  * `StarPiece` (up to 82)
  * `ThreeStarPieces` (up to 5)
  * `PowerStar` (up to 120)
* Regular Consumables
  * `DriedShroom`
  * `Mushroom`
  * `SuperShroom`
  * `UltraShroom`
  * `VoltShroom`
  * `LifeShroom`
  * `Apple`
  * `Egg`
  * `IcedPotato`
  * `Melon`
  * `DriedFruit`
  * `HoneySyrup`
  * `MapleSyrup`
  * `JamminJelly`
  * `SuperSoda`
  * `Lime`
  * `Goomnut`
  * `KoopaLeaf`
  * `StrangeLeaf`
  * `StinkyHerb`
  * `CakeMix`
  * `Lemon`
  * `DriedPasta`
  * `WhackasBump`
  * `BlueBerry`
  * `RedBerry`
  * `YellowBerry`
  * `BubbleBerry`
  * `TastyTonic`
  * `Pebble`
  * `DustyHammer`
  * `Coconut`
  * `POWBlock`
  * `FireFlower`
  * `SnowmanDoll`
  * `ThunderBolt`
  * `ThunderRage`
  * `ShootingStar`
  * `Mystery`
  * `StoneCap`
  * `StopWatch`
  * `SleepySheep`
  * `DizzyDial`
  * `FrightJar`
  * `RepelGel`
  * `InsecticideHerb`
  * `HustleDrink`
* Tayce T. Consumables
  * `FriedShroom`
  * `SpicySoup`
  * `ApplePie`
  * `NuttyCake`
  * `HoneyShroom`
  * `MapleShroom`
  * `JellyShroom`
  * `HoneySuper`
  * `MapleSuper`
  * `JellySuper`
  * `HoneyUltra`
  * `MapleUltra`
  * `JellyUltra`
  * `Cake`
  * `ShroomCake`
  * `StrangeCake`
  * `BoiledEgg`
  * `EggMissile`
  * `FriedEgg`
  * `Koopasta`
  * `ShroomSteak`
  * `HotShroom`
  * `SweetShroom`
  * `BlandMeal`
  * `YummyMeal`
  * `DeluxeFeast`
  * `HealthyJuice`
  * `SpecialShake`
  * `BigCookie`
  * `YoshiCookie`
  * `KookyCookie`
  * `KoopaTea`
  * `Spaghetti`
  * `HoneyCandy`
  * `LimeCandy`
  * `LemonCandy`
  * `ElectroPop`
  * `FirePop`
  * `CocoPop`
  * `JellyPop`
  * `FrozenFries`
  * `PotatoSalad`
  * `Mistake`
