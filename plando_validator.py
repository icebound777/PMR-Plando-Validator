"""
Validator module for the Paper Mario Randomizer plandomizer file.
"""

import json


TOPLEVEL_FIELD_DIFFICULTY = "difficulty"
TOPLEVEL_FIELD_MOVE_COSTS = "move_costs"


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