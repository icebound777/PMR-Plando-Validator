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
