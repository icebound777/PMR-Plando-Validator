"""
Validator module for the Paper Mario Randomizer plandomizer file.
"""

from functools import reduce
import re
import json

from .plando_metadata import (
    allowed_locations,
    shop_locations,
    disallowed_shop_locations,
    allowed_items,
    block_locations,
    limited_items,
    progressive_badges,
    forbidden_trap_locations,
    force_puzzlerando_locations,
)


TOPLEVEL_FIELD_DIFFICULTY = "difficulty"
TOPLEVEL_FIELD_MOVE_COSTS = "move_costs"
TOPLEVEL_FIELD_BOSS_BATTLES = "boss_battles"
TOPLEVEL_FIELD_REQUIRED_SPIRITS = "required_spirits"
TOPLEVEL_FIELD_ITEMS = "items"


def validate_from_filepath(
    file_path: str
) -> tuple[dict, dict]:
    """
    Tries do decode a file at the provided file path as JSON.
    If successful, passes that JSON dict to the ``validate_from_dict`` function,
    and returns that function's data.
    """
    plando_data: dict = dict()

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            plando_data = json.load(file)
    except json.decoder.JSONDecodeError as err:
        return {}, {"warnings": [], "errors": [f"Could not decode JSON! {err}"]}

    return validate_from_dict(plando_data)


def validate_from_dict(
    plando_data: dict
) -> tuple[dict, dict]:
    """
    Validate and parse the provided ``plando_data`` dictionary according to a
    defined set of rules, then return the parsed data if not errors occured.
    Any warnings and errors get collected and returned as a second dict.
    """
    parsed_data: dict = dict()
    messages: dict[str, list[str]] = dict()

    implemented_toplevel_fields: list[str] = [
        TOPLEVEL_FIELD_DIFFICULTY,
        TOPLEVEL_FIELD_MOVE_COSTS,
        TOPLEVEL_FIELD_BOSS_BATTLES,
        TOPLEVEL_FIELD_REQUIRED_SPIRITS,
        TOPLEVEL_FIELD_ITEMS,
    ]

    messages["warnings"] = list()
    messages["errors"] = list()
    messages_wrn = messages["warnings"]
    messages_err = messages["errors"]
    ret_tuple = parsed_data, messages

    if not plando_data:
        err_msg = "Provided plando_data is empty"
        messages_err.append(err_msg)
        return ret_tuple

    for k in plando_data:
        if not isinstance(k, str):
            messages_err.append(f"Plando data includes top level field of wrong type (expected str): \"{k}\" ({type(k)})")
        elif k not in implemented_toplevel_fields:
            messages_wrn.append(f"Plando data includes unhandled top level field: \"{k}\"")

        elif k == TOPLEVEL_FIELD_DIFFICULTY:
            if plando_data[k] is not None and not isinstance(plando_data[k], dict):
                messages_err.append(f"Top-level key has wrong data type (expected dict or null): \"{plando_data[k]}\" ({type(plando_data[k])})")
                continue
            difficulties, new_wrns, new_errs = _get_difficulty(plando_data[k])

            parsed_data[TOPLEVEL_FIELD_DIFFICULTY] = difficulties
            messages_wrn.extend(new_wrns)
            messages_err.extend(new_errs)

        elif k == TOPLEVEL_FIELD_MOVE_COSTS:
            if plando_data[k] is not None and not isinstance(plando_data[k], dict):
                messages_err.append(f"Top-level key has wrong data type (expected dict or null): \"{plando_data[k]}\" ({type(plando_data[k])})")
                continue
            move_costs, new_wrns, new_errs = _get_move_costs(plando_data[k])

            parsed_data[TOPLEVEL_FIELD_MOVE_COSTS] = move_costs
            messages_wrn.extend(new_wrns)
            messages_err.extend(new_errs)

        elif k == TOPLEVEL_FIELD_BOSS_BATTLES:
            if plando_data[k] is not None and not isinstance(plando_data[k], dict):
                messages_err.append(f"Top-level key has wrong data type (expected dict or null): \"{plando_data[k]}\" ({type(plando_data[k])})")
                continue
            boss_battles, new_wrns, new_errs = _get_boss_battles(plando_data[k])

            parsed_data[TOPLEVEL_FIELD_BOSS_BATTLES] = boss_battles
            messages_wrn.extend(new_wrns)
            messages_err.extend(new_errs)

        elif k == TOPLEVEL_FIELD_REQUIRED_SPIRITS:
            if plando_data[k] is not None and not isinstance(plando_data[k], list):
                messages_err.append(f"Top-level key has wrong data type (expected list or null): \"{plando_data[k]}\" ({type(plando_data[k])})")
                continue
            required_spirits, new_wrns, new_errs = _get_required_spirits(plando_data[k])

            parsed_data[TOPLEVEL_FIELD_REQUIRED_SPIRITS] = required_spirits
            messages_wrn.extend(new_wrns)
            messages_err.extend(new_errs)

        elif k == TOPLEVEL_FIELD_ITEMS:
            if plando_data[k] is not None and not isinstance(plando_data[k], dict):
                messages_err.append(f"Top-level key has wrong data type (expected dict or null): \"{plando_data[k]}\" ({type(plando_data[k])})")
                continue
            item_placement, new_wrns, new_errs = _get_item_placement(plando_data[k])

            parsed_data[TOPLEVEL_FIELD_ITEMS] = item_placement
            messages_wrn.extend(new_wrns)
            messages_err.extend(new_errs)

    if messages_err:
        parsed_data.clear()

    return ret_tuple


def _get_difficulty(
    difficulties: dict[str, int] | None
) -> tuple[dict[int, int], list[str], list[str]]:
    """
    Validates and parses chapter difficulties.
    The allowed chapters to set are ch1-ch7, and the allowed difficulty
    values are 1-8.
    Warnings are caused by: Valid but disallowed keys (get ignored), setting
    the difficulty of any possible starting chapter over difficulty 3.
    Errors are caused by: Wrong datatypes for keys or values, setting a
    difficulty value outside of the allowed range.
    """
    parsed_difficulties: dict[int, int] = dict()
    new_wrns: list[str] = list()
    new_errs: list[str] = list()

    if difficulties is None:
        return parsed_difficulties, new_wrns, new_errs

    allowed_keys = [
        "chapter 1",
        "chapter 2",
        "chapter 3",
        "chapter 4",
        "chapter 5",
        "chapter 6",
        "chapter 7",
    ]
    allowed_values = [1,2,3,4,5,6,7,8]

    starting_chapters = ["chapter 1", "chapter 2", "chapter 5"]

    for k, v in difficulties.items():
        # Check datatypes for key and value
        new_err_found = False
        if not isinstance(k, str):
            new_errs.append(f"difficulty: Key has wrong data type (expected str): \"{k}\" ({type(k)})")
            new_err_found = True
        if v is not None and not isinstance(v, int):
            new_errs.append(f"difficulty: Value has wrong data type (expected int or null): \"{v}\" ({type(v)})")
            new_err_found = True
        if new_err_found:
            continue

        # Check if key and value are in allowed ranges
        if k not in allowed_keys:
            new_wrns.append(f"difficulty: Found unexpected Key: \"{k}\" (not one of {allowed_keys=})")
            continue
        if v is not None and v not in allowed_values:
            new_errs.append(f"difficulty: Found disallowed Value: {v} (not one of {allowed_values=} or null)")
            continue

        # Check if value is unset
        if v is None:
            continue

        # Check if key is a starting chapter and value is over difficulty 3
        if k in starting_chapters and v > 3:
            new_wrns.append(f"difficulty: {k} is scaled higher than difficulty 3. Beware if this is the starting location")

        parsed_difficulties[int(k[-1:])] = v

    return parsed_difficulties, new_wrns, new_errs


def _get_move_costs(
    move_costs: dict[str, dict[str, dict[str, int | None]]] | None
) -> dict[str, dict[str, dict[str, int]]]:
    """
    Validates and parses the BP-, FP-, and SP-costs for badges, moves (both
    Mario and partners), and star powers.
    The allowed values are: BP 0-10, FP 1-10, SP 1-7.
    Warnings are caused by: Valid but disallowed keys (get ignored), setting
    FP cost to zero (as this can cause unexpected reordering of menu items in
    battle).
    Errors are caused by: Wrong datatypes for keys or values, setting a
    move cost value outside of the allowed range.
    """
    # dict[move_type, dict[move_name, dict[move_cost_type, move_cost]]]
    # to mimic the layout within the sqlite db's 'move' table.
    # also starpower cost are 'FP', for reasons
    parsed_move_costs: dict[str, dict[str, dict[str, int]]] = dict()

    new_wrns: list[str] = list()
    new_errs: list[str] = list()

    if move_costs is None:
        return parsed_move_costs, new_wrns, new_errs

    allowed_toplevel_keys = [
        "badge",
        "partner",
        "starpower"
    ]

    allowed_badge_keys = {
        "AllorNothing": ["BP"],
        "AutoJump": ["BP","FP"],
        "AutoSmash": ["BP","FP"],
        "Autobounce": ["BP","FP"],
        "Berserker": ["BP"],
        "BumpAttack": ["BP"],
        "ChillOut": ["BP"],
        "CloseCall": ["BP"],
        "CrazyHeart": ["BP"],
        "DDownJump": ["BP","FP"],
        "DDownPound": ["BP","FP"],
        "DamageDodge": ["BP"],
        "DeepFocus": ["BP"],
        "DefendPlus": ["BP"],
        "DizzyAttack": ["BP"],
        "DizzyStomp": ["BP","FP"],
        "DodgeMaster": ["BP"],
        "DoubleDip": ["BP","FP"],
        "FPPlus": ["BP"],
        "FeelingFine": ["BP"],
        "FireShield": ["BP"],
        "FirstAttack": ["BP"],
        "FlowerFanatic": ["BP"],
        "FlowerFinder": ["BP"],
        "FlowerSaver": ["BP"],
        "GroupFocus": ["BP"],
        "HPDrain": ["BP"],
        "HPPlus": ["BP"],
        "HammerThrow": ["BP","FP"],
        "HappyFlower": ["BP"],
        "HappyHeart": ["BP"],
        "HealthyHealthy": ["BP"],
        "HeartFinder": ["BP"],
        "ISpy": ["BP"],
        "IcePower": ["BP"],
        "JumpCharge": ["BP","FP"],
        "LastStand": ["BP"],
        "LuckyDay": ["BP"],
        "MegaHPDrain": ["BP"],
        "MegaJump": ["BP","FP"],
        "MegaQuake": ["BP","FP"],
        "MegaRush": ["BP"],
        "MegaSmash": ["BP","FP"],
        "MiniJumpCharge": ["BP","FP"],
        "MiniSmashCharge": ["BP","FP"],
        "MoneyMoney": ["BP"],
        "Multibounce": ["BP","FP"],
        "PDownDUp": ["BP"],
        "PUpDDown": ["BP"],
        "PayOff": ["BP"],
        "Peekaboo": ["BP"],
        "PowerBounce": ["BP","FP"],
        "PowerJump": ["BP","FP"],
        "PowerPlus": ["BP"],
        "PowerQuake": ["BP","FP"],
        "PowerRush": ["BP"],
        "PowerSmash": ["BP","FP"],
        "PrettyLucky": ["BP"],
        "QuakeBounce": ["BP","FP"],
        "QuakeHammer": ["BP","FP"],
        "QuickChange": ["BP"],
        "Refund": ["BP"],
        "RightOn": ["BP"],
        "RunawayPay": ["BP"],
        "ShrinkSmash": ["BP","FP"],
        "ShrinkStomp": ["BP","FP"],
        "SleepStomp": ["BP","FP"],
        "SmashCharge": ["BP","FP"],
        "SpeedySpin": ["BP"],
        "SpikeShield": ["BP"],
        "SpinAttack": ["BP"],
        "SpinSmash": ["BP","FP"],
        "SuperFocus": ["BP"],
        "SuperJump": ["BP","FP"],
        "SuperJumpCharge": ["BP","FP"],
        "SuperSmash": ["BP","FP"],
        "SuperSmashCharge": ["BP","FP"],
        "TripleDip": ["BP","FP"],
        "ZapTap": ["BP"],
    }

    allowed_partner_keys = {
        "Goombario": ["Charge","Multibonk"],
        "Kooper": ["PowerShell","DizzyShell","FireShell"],
        "Bombette": ["Bomb","PowerBomb","MegaBomb"],
        "Parakarry": ["ShellShot","AirLift","AirRaid"],
        "Bow": ["OuttaSight","Spook","FanSmack"],
        "Watt": ["PowerShock","TurboCharge","MegaShock"],
        "Sushie": ["Squirt","WaterBlock","TidalWave"],
        "Lakilester": ["SpinySurge","CloudNine","Hurricane"]
    }

    allowed_starpower_keys = [
        "Refresh",
        "Lullaby",
        "StarStorm",
        "ChillOut",
        "Smooch",
        "TimeOut",
        "UpAndAway",
    ]

    allowed_costs_bp = [0,1,2,3,4,5,6,7,8,9,10]
    allowed_costs_fp = range(0, 76)
    allowed_costs_sp = [0,1,2,3,4,5,6,7]

    for k, v in move_costs.items():
        # Check datatypes for top-level key and value
        new_err_found = False
        if not isinstance(k, str):
            new_errs.append(f"move_costs: Top-level key has wrong data type (expected str): \"{k}\" ({type(k)})")
            new_err_found = True
        if v is not None and not isinstance(v, dict):
            new_errs.append(f"move_costs: Top-level value has wrong data type (expected dict or null): \"{v}\" ({type(v)})")
            new_err_found = True
        if new_err_found:
            continue

        # Check if top-level key is in allowed ranged
        if k not in allowed_toplevel_keys:
            new_wrns.append(f"move_costs: Found unexpected Top-level key: \"{k}\" (not one of {allowed_toplevel_keys=})")
            continue
        elif v is not None:
            # Check datatypes for mid-level key and value
            if not isinstance(v, dict):
                new_errs.append(f"move_costs: Mid-level value for \"{k}\" key has wrong data type (expected dict or null): \"{v}\" ({type(v)})")

            if k == "badge":
                for badge_name, badge_dict in move_costs[k].items():
                    # Check datatypes for badges key and value
                    if not isinstance(badge_name, str):
                        new_wrns.append(f"move_costs: Badge name key \"{badge_name}\" has wrong data type (expected str): \"{badge_name}\" ({type(badge_name)})")
                        continue
                    if badge_dict is not None and not isinstance(badge_dict, dict):
                        new_errs.append(f"move_costs: Mid-level value for badge name key \"{badge_name}\" has wrong data type (expected dict or null): \"{badge_dict}\" ({type(badge_dict)})")
                        continue

                    # Check if value is unset
                    if badge_dict is None:
                        continue

                    # Check if badge key is in allowed list
                    if badge_name not in allowed_badge_keys:
                        new_wrns.append(f"move_costs: Badge name key \"{badge_name}\" is not a valid badge name")
                        continue

                    # Check for allowed badge costs
                    for badge_cost_type, badge_cost in badge_dict.items():
                        # Check badge cost data types
                        if not isinstance(badge_cost_type, str):
                            new_errs.append(f"move_costs: Badge cost type of badge \"{badge_name}\" has wrong data type (expected str): \"{badge_cost_type}\" ({type(badge_cost_type)})")
                            continue
                        if badge_cost is not None and not isinstance(badge_cost, int):
                            new_errs.append(f"move_costs: Badge cost of badge \"{badge_name}\" has wrong data type (expected int): \"{badge_cost}\" ({type(badge_cost)})")
                            continue

                        # Check badge cost allowed ranges
                        if badge_cost_type not in allowed_badge_keys[badge_name]:
                            new_wrns.append(f"move_costs: Badge cost type \"{badge_cost_type}\" of badge \"{badge_name}\" is not a valid cost type for this badge")
                            continue
                        if badge_cost is not None and badge_cost_type == "BP" and badge_cost not in allowed_costs_bp:
                            new_errs.append(f"move_costs: Found disallowed Value: Badge cost \"{badge_cost}\" of badge \"{badge_name}:{badge_cost_type}\" (not one of {allowed_costs_bp=} or null)")
                            continue
                        if badge_cost is not None and badge_cost_type == "FP" and badge_cost not in allowed_costs_fp:
                            new_errs.append(f"move_costs: Found disallowed Value: Badge cost \"{badge_cost}\" of badge \"{badge_name}:{badge_cost_type}\" (not one of {allowed_costs_fp=} or null)")
                            continue

                        # Check if value is unset
                        if badge_cost is None:
                            continue

                        if k not in parsed_move_costs:
                            parsed_move_costs[k] = dict()
                        if badge_name not in parsed_move_costs[k]:
                            parsed_move_costs[k][badge_name] = dict()
                        parsed_move_costs[k][badge_name][badge_cost_type] = badge_cost

            elif k == "partner":
                for partner_name, partner_dict in move_costs[k].items():
                    # Check datatypes for partners key and value
                    if not isinstance(partner_name, str):
                        new_wrns.append(f"move_costs: partner name key \"{partner_name}\" has wrong data type (expected str): \"{partner_name}\" ({type(partner_name)})")
                        continue
                    if partner_dict is not None and not isinstance(partner_dict, dict):
                        new_errs.append(f"move_costs: Mid-level value for partner name key \"{partner_name}\" has wrong data type (expected dict or null): \"{partner_dict}\" ({type(partner_dict)})")
                        continue

                    # Check if value is unset
                    if partner_dict is None:
                        continue

                    # Check if partner key is in allowed list
                    if partner_name not in allowed_partner_keys:
                        new_wrns.append(f"move_costs: partner name key \"{partner_name}\" is not a valid partner name")
                        continue

                    # Check for allowed partner move costs
                    for partner_move, partner_move_cost in partner_dict.items():
                        # Check partner_dict data types
                        if not isinstance(partner_move, str):
                            new_errs.append(f"move_costs: partner move of partner \"{partner_name}\" has wrong data type (expected str): \"{partner_move}\" ({type(partner_move)})")
                            continue
                        if partner_move_cost is not None and not isinstance(partner_move_cost, int):
                            new_errs.append(f"move_costs: partner move cost of \"{partner_name}:{partner_move}\" has wrong data type (expected int): \"{partner_move_cost}\" ({type(partner_move_cost)})")
                            continue

                        # Check valid partner moves and allowed ranges
                        if partner_move not in allowed_partner_keys[partner_name]:
                            new_wrns.append(f"move_costs: partner move \"{partner_move}\" of partner \"{partner_name}\" is not a valid move for this partners")
                            continue
                        if partner_move_cost is not None and partner_move_cost not in allowed_costs_fp:
                            new_errs.append(f"move_costs: Found disallowed Value: partner move cost \"{partner_move_cost}\" of partner \"{partner_name}\" (not one of {allowed_costs_fp=} or null)")
                            continue

                        if partner_move_cost == 0:
                            new_wrns.append(f"move_costs: FP cost of \"{partner_name}:{partner_move}\" set to zero. This will cause weirdness in battle menues.")

                        # Check if value is unset
                        if partner_move_cost is None:
                            continue

                        if k not in parsed_move_costs:
                            parsed_move_costs[k] = dict()
                        if partner_move not in parsed_move_costs[k]:
                            parsed_move_costs[k][partner_move] = dict()
                        parsed_move_costs[k][partner_move]["FP"] = partner_move_cost

            elif k == "starpower":
                for starpower_name, starpower_cost in move_costs[k].items():
                    # Check datatypes for starpowers key and value
                    if not isinstance(starpower_name, str):
                        new_wrns.append(f"move_costs: starpower name key \"{starpower_name}\" has wrong data type (expected str): \"{starpower_name}\" ({type(starpower_name)})")
                        continue
                    if starpower_cost is not None and not isinstance(starpower_cost, int):
                        new_errs.append(f"move_costs: value for starpower cost of \"{starpower_name}\" has wrong data type (expected int or null): \"{starpower_cost}\" ({type(starpower_cost)})")
                        continue

                    # Check if starpower key is in allowed list
                    if starpower_name not in allowed_starpower_keys:
                        new_wrns.append(f"move_costs: starpower name key \"{starpower_name}\" is not a valid starpower name")
                        continue

                    # Check starpower cost allowed ranges
                    if starpower_cost is not None and starpower_cost not in allowed_costs_sp:
                        new_errs.append(f"move_costs: Found disallowed Value: starpower cost \"{starpower_cost}\" of starpower \"{starpower_name}\" (not one of {allowed_costs_sp=} or null)")
                        continue

                    # Check if value is unset
                    if starpower_cost is None:
                        continue

                    if k not in parsed_move_costs:
                        parsed_move_costs[k] = dict()
                    parsed_move_costs[k][starpower_name] = dict()
                    parsed_move_costs[k][starpower_name]["FP"] = starpower_cost

    return parsed_move_costs, new_wrns, new_errs


def _get_boss_battles(
    boss_battles: dict[str, str] | None
) -> tuple[dict[int, int], list[str], list[str]]:
    """
    Validates and parses boss battles.
    The allowed chapters to set are ch1-ch7, and the allowed bosses are Koopa
    Bros., Tutankoopa, Tubba's Heart, General Guy, Lava Piranha, Huff n Puff,
    and Crystal King.
    Warnings are caused by: Valid but disallowed keys (get ignored), setting any
    boss at all (due to scaling oddities when bosses appear multiple times)
    Errors are caused by: Wrong datatypes for keys or values, setting a
    boss that's not recognized
    """
    parsed_boss_battles: dict[int, int] = dict()

    new_wrns: list[str] = list()
    new_errs: list[str] = list()

    if boss_battles is None:
        return parsed_boss_battles, new_wrns, new_errs

    allowed_keys = [
        "chapter 1",
        "chapter 2",
        "chapter 3",
        "chapter 4",
        "chapter 5",
        "chapter 6",
        "chapter 7",
    ]
    allowed_values = [
        "KoopaBros",
        "Tutankoopa",
        "TubbasHeart",
        "GeneralGuy",
        "LavaPiranha",
        "HuffNPuff",
        "CrystalKing",
    ]

    for k, v in boss_battles.items():
        # Check datatypes for key and value
        new_err_found = False
        if not isinstance(k, str):
            new_errs.append(f"boss_battles: key has wrong data type (expected str): \"{k}\" ({type(k)})")
            new_err_found = True
        if v is not None and not isinstance(v, str):
            new_errs.append(f"boss_battles: value has wrong data type (expected str or null): \"{v}\" ({type(v)})")
            new_err_found = True
        if new_err_found:
            continue

        # Check if key and value are in allowed ranges
        if k not in allowed_keys:
            new_wrns.append(f"boss_battles: found unexpected Key: \"{k}\" (not one of {allowed_keys=})")
            continue
        if v is not None and v not in allowed_values:
            new_errs.append(f"boss_battles: found disallowed Value: {v} (not one of {allowed_values=} or null)")
            continue

        # Check if value is unset
        if v is None:
            continue

        parsed_boss_battles[int(k[-1:])] = allowed_values.index(v) + 1

    if parsed_boss_battles and len(set(list(parsed_boss_battles.values()))) != 7:
        new_wrns.append(f"boss_battles: not all 7 bosses are plando'd. "
            "Beware of scaling oddities if a boss appears multiple times if progressive scaling is turned off"
        )

    return parsed_boss_battles, new_wrns, new_errs


def _get_required_spirits(
    required_spirits: list[str | int] | None
) -> tuple[list[int], list[str], list[str]]:
    """
    Validates and parses specific spirits to save for opening Star Way.
    Any of the seven star spirits can be set, with the allowed values of
    Eldstar, Mamar, Skolar, Muskular, Misstar, Klevar, and Kalmer, or just
    using the chapter numbers.
    Warnings are caused by: Valid but duplicate keys (get ignored), setting all
    seven spirits (turns off ``Require Specific Spirits``), setting any spirit
    at all (due to interactions with ``Require Specific Spirits`` and
    ``Star Way Spirits Needed`` that the user should be aware of)
    Errors are caused by: Wrong datatypes for keys or values, setting a
    star spirit that's not recognized
    """
    parsed_required_spirits: list[int] = list()

    new_wrns: list[str] = list()
    new_errs: list[str] = list()

    if required_spirits is None:
        return parsed_required_spirits, new_wrns, new_errs

    allowed_values: dict[str | int, int] = {
        "Eldstar": 1,
        "Mamar": 2,
        "Skolar": 3,
        "Muskular": 4,
        "Misstar": 5,
        "Klevar": 6,
        "Kalmar": 7,
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
    }

    for k in required_spirits:
        # Check if value is unset
        if k is None:
            continue

        # Check datatypes for key
        if not isinstance(k, str) and not isinstance(k, int):
            new_errs.append(f"required_spirits: key has wrong data type (expected str or int): \"{k}\" ({type(k)})")
            continue

        # Check if key is in allowed ranges
        if k not in allowed_values:
            new_errs.append(f"required_spirits: found unexpected key: \"{k}\" (not one of {allowed_values.keys()=})")
            continue

        if allowed_values[k] in parsed_required_spirits:
            new_wrns.append(f"required_spirits: spirit number \"{allowed_values[k]}\" set multiple times, ignoring")
        else:
            parsed_required_spirits.append(allowed_values[k])

    if len(parsed_required_spirits) >= 7:
        new_wrns.append(f"required_spirits: all spirits required, this will turn off 'Require Specific Spirits'")
    if len(parsed_required_spirits) > 0:
        new_wrns.append(
            f"required_spirits: spirits are set, this will overrule 'Star Way Spirits Needed' "
            f"if more spirits are set than needed for Star Way. Set spirits will be ignored if "
            f"'Require Specific Spirits' is turned off"
        )

    parsed_required_spirits.sort()

    return parsed_required_spirits, new_wrns, new_errs


def _get_item_placement(
    item_areas: dict[str, dict[str, str | None | dict[str, str | int | None]]] | None
) -> tuple[list[int], list[str], list[str]]:
    """
    Validates and parses item placement.
    Item placement is subject to certain restrictions, which the seed generator
    has to abide by as well. Certain items can be places unlimited times, while
    others have an upper maximum count. Placing certain items manually will also
    force active certain seed settings the placed item relies upon.

    Warnings are caused by: Valid but disallowed areas or item locations (get
    ignored), passing an unused key in as shop dict, placing items in locations
    that currently cannot be plando'd, placing badges of the badge families that
    have progressive badge equivalents (force-deactivates Progressive Badges),
    placing progressive badges (force-activates Progressive Badges), placing
    partner upgrade items (force-activates Partern Upgrade Shuffle), placing
    more than 34 starpieces, placing items into the Dry Dry Outpost shop spots
    where the shop code items usually are (force-activates Random Puzzles).

    Errors are caused by: Wrong datatypes for keys or values, setting item
    prices for non-shop locations or for shops with static prices, setting item
    prices outside of the allowed range, placing an unrecognized item or trap,
    placing a trap into a location that cannot handle trap items, placing both
    badges of the badge families that have progressive badge equivalents and
    their progressive badge counterparts, placing a limited item more often than
    allowed.
    """
    new_wrns: set[str] = set()
    new_errs: list[str] = list()
    parsed_item_placement: dict[str, dict[str, int | str]] = dict()

    if item_areas is None:
        return parsed_item_placement, list(new_wrns), new_errs

    track_placed_items: dict[str, list] = dict()

    def _try_placing_item(
        ref_item_placement_dict: dict,
        area_key: str,
        item_location: str,
        item_name: str,
        shop_data_key: str | None = None,
    ) -> tuple[list[str], list[str]]:
        placement_wrns: list[str] = list()
        placement_errs: list[str] = list()

        placement_okay = True

        # Check: Is item allowed to be placed here?
        ## Block locations cannot be set
        if area_key in block_locations and item_location in block_locations[area_key]:
            placement_okay = False
            placement_wrns.append(f"items: location \"{area_key}:{item_location}\" cannot be plando'd at the moment and is ignored")

        ## Item is trap and location cannot hold traps
        if (    item_name.startswith("TRAP")
            and (   (    area_key in shop_locations
                     and item_location in shop_locations[area_key])
                 or item_location in forbidden_trap_locations
            )
        ):
            placement_okay = False
            placement_errs.append(f"items: location \"{area_key}:{item_location}\" cannot hold traps")

        # Check: Specific trap item is a valid item
        if item_name.startswith("TRAP") and item_name != "TRAP":
            regex_match = re.match(r"TRAP \((.*)\)", item_name)
            specific_trap = regex_match.group(1)
            if specific_trap is None:
                placement_okay = False
                placement_errs.append(f"items: location \"{area_key}:{item_location}\" has trap set that's not recognized: \"{item_name}\"")
            elif specific_trap not in allowed_items:
                placement_okay = False
                placement_errs.append(f"items: location \"{area_key}:{item_location}\" has trap set that is not an allowed item: \"{item_name}\"")

        # Check: Progressive badge families being placed manually
        if item_name in progressive_badges["originals"]:
            if any([x for x in progressive_badges["progressives"] if x in track_placed_items]):
                placement_okay = False
                placement_errs.append(f"items: cannot place both progressive and non-progressive badges")
            else:
                placement_wrns.append(f"items: badge \"{item_name}\" is manually set: This turns off Progressive Badges")
        if item_name in progressive_badges["progressives"]:
            if any([x for x in progressive_badges["originals"] if x in track_placed_items]):
                placement_okay = False
                placement_errs.append(f"items: cannot place both progressive and non-progressive badges")
            else:
                placement_wrns.append(f"items: badge \"{item_name}\" is manually set: This turns on Progressive Badges")

        # Check: Partner Upgrade items and warn that they turn on their setting
        if item_name.endswith("Upgrade"):
            placement_wrns.append(f"items: placing partner upgrade will turn on Partner Upgrade Shuffle")

        # Check: Did we already exceed the number of intances allowed for this item?
        if item_name in limited_items and item_name in track_placed_items:
            if track_placed_items[item_name] >= limited_items[item_name]:
                placement_okay = False
                placement_errs.append(f"items: \"{item_name}\" placed more often than allowed. max: {limited_items[item_name]}")

            ## Check: If star pieces, check numbers for warning thresholds
            if item_name == "StarPiece" and 34 < track_placed_items[item_name]:
                placement_wrns.append("items: placed more than 34 star pieces: Depending on settings this can lead to weird vanilla star piece locations")


        if placement_okay:
            if area_key not in ref_item_placement_dict:
                ref_item_placement_dict[area_key] = dict()
            if shop_data_key is None:
                ref_item_placement_dict[area_key][item_location] = item_name
                if item_name not in track_placed_items:
                    track_placed_items[item_name] = 1
                else:
                    track_placed_items[item_name] += 1
            else:
                if item_location not in ref_item_placement_dict[area_key]:
                    ref_item_placement_dict[area_key][item_location] = dict()
                ref_item_placement_dict[area_key][item_location][shop_data_key] = item_name

        return placement_wrns, placement_errs


    for area_key, v in item_areas.items():
        # Check datatypes for top-level key and values
        new_err_found = False
        if not isinstance(area_key, str):
            new_errs.append(f"items: key has wrong data type (expected str): \"{area_key}\" ({type(area_key)})")
            new_err_found = True
        if v is not None and not isinstance(v, dict):
            new_errs.append(f"items: value has wrong data type (expected dict): \"{v}\" ({type(v)})")
            new_err_found = True
        if new_err_found:
            continue

        # Check if key is an allowed area name
        if area_key not in allowed_locations:
            new_wrns.add(f"items: found unexpected key: \"{area_key}\" (not one of {allowed_locations.keys()=})")
            continue

        # Check if value is unset
        if v is None:
            continue

        for item_location, item_or_shopdict in v.items():
            # Check datatypes for item location key and values
            new_err_found = False
            if not isinstance(item_location, str):
                new_errs.append(f"items: item location has wrong data type (expected str): \"{item_location}\" ({type(item_location)})")
                new_err_found = True
            if (    item_or_shopdict is not None
                and not isinstance(item_or_shopdict, (str, dict))
            ):
                new_errs.append(f"items: item has wrong data type (expected str, dict or null): \"{item_or_shopdict}\" ({type(item_or_shopdict)})")
                new_err_found = True
            if new_err_found:
                continue

            # Check if item location key is an allowed item location
            if item_location not in allowed_locations[area_key]:
                new_wrns.add(f"items: found unexpected item location: \"{item_location}\" (not part of \"{area_key}\")")
                continue

            # Check if value is unset
            if item_or_shopdict is None:
                continue

            if isinstance(item_or_shopdict, dict):
                # Check if this location even is a shop
                if not item_location in shop_locations[area_key]:
                    new_errs.append(f"items: item location \"{item_location}\" is not a shop, but \"{item_or_shopdict}\" is a dict")
                    continue
                # Check if someone tries setting the prices for Merlow
                if (    area_key in disallowed_shop_locations
                    and item_location in disallowed_shop_locations[area_key]
                ):
                    new_errs.append(f"items: item location \"{item_location}\" is not a shop you can set the item price for (should be str instead)")
                    continue

                for key, val in item_or_shopdict.items():
                    new_err_found = False
                    if not isinstance(key, str):
                        new_errs.append(f"items: shop-dict key has wrong data type (expected str): \"{key}\" ({type(key)})")
                        new_err_found = True
                    if val is not None and not isinstance(val, (str, int)):
                        new_errs.append(f"items: shop-dict value has wrong data type (expected str, int or null): \"{val}\" ({type(val)})")
                        new_err_found = True
                    if new_err_found or val is None:
                        continue

                    # Check if value is allowed for this key
                    if key not in ["item", "price"]:
                        new_wrns.add(f"items: found unexpected key \"{key}\"in item location: \"{item_location}\" (not one of ['item','price'])")

                    if key == "price":
                        if not isinstance(val, int):
                            new_errs.append(f"items: shop-price for \"{item_location}\" has wrong data type (expected int or null): \"{val}\" ({type(val)})")
                            continue
                        if not 0 <= val <= 999:
                            new_errs.append(f"items: shop-price for \"{item_location}\" is outside of allowed range of 0-999: \"{val}\")")
                            continue

                        #+ Add item price here
                        if area_key not in parsed_item_placement:
                            parsed_item_placement[area_key] = dict()
                        if item_location not in parsed_item_placement[area_key]:
                            parsed_item_placement[area_key][item_location] = dict()
                        parsed_item_placement[area_key][item_location][key] = val

                    else: # key == "item"
                        if not isinstance(val, str):
                            new_errs.append(f"items: shop item for \"{item_location}\" has wrong data type (expected str or null): \"{val}\" ({type(val)})")
                            continue

                        # Check if item can be set
                        if val not in allowed_items and not item_or_shopdict.startswith("TRAP ("):
                            new_errs.append(f"items: found unexpected item at \"{item_location}\": \"{val}\"")
                            continue

                        # Check if location is one of the Dry Dry Outpost code spots
                        if item_location in force_puzzlerando_locations:
                            new_wrns.add("items: item placed into Dry Dry Outpost shop code location: This may force on Random Puzzles")

                        # Special item placement checks
                        placement_wrns, placement_errs = _try_placing_item(
                            parsed_item_placement,
                            area_key,
                            item_location,
                            val,
                            key,
                        )
                        for wrn in placement_wrns:
                            new_wrns.add(wrn)
                        new_errs.extend(placement_errs)

            else: # has to be str
                item_name = item_or_shopdict
                # Check if item can be set
                if item_name not in allowed_items and not item_name.startswith("TRAP ("):
                    new_errs.append(f"items: found unexpected item at \"{item_location}\": \"{item_name}\"")
                    continue

                # Special item placement checks
                placement_wrns, placement_errs = _try_placing_item(
                    parsed_item_placement,
                    area_key,
                    item_location,
                    item_name,
                )
                for wrn in placement_wrns:
                    new_wrns.add(wrn)
                new_errs.extend(placement_errs)

    return parsed_item_placement, list(new_wrns), new_errs
