"""
Validator module for the Paper Mario Randomizer plandomizer file.
"""

import json


TOPLEVEL_FIELD_DIFFICULTY = "difficulty"


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
            if not isinstance(plando_data[k], dict):
                messages_err.append(f"Top-level key has wrong data type (expected dict or null): \"{plando_data[k]}\" ({type(plando_data[k])})")
                continue
            difficulties, new_wrns, new_errs = _get_difficulty(plando_data[k])

            parsed_data[TOPLEVEL_FIELD_DIFFICULTY] = difficulties
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
