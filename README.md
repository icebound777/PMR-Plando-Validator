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
* The difficulty section gets ignored if the `Progressive Scaling` option is active
