"""
autocorrect.py - Methodology to attempt auto-correcting a typo'd system name.

Copyright (c) 2019 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import re


def correct_system_name(system: str) -> str:
    """
    Take a system name and attempt to correct common mistakes to get the true system name.

    Args:
        system (str): The system name to check for corrections.

    Returns:
        str: The system name with any corrections applied, uppercased.
    """
    system = system.upper()
    match_regex = re.compile(r"(.*)\b([A-Z01258]{2}-[A-Z01258])\s+"
                             r"([A-Z01258])\s*([0-9OIZSB]+(-[0-9OIZSB]+)?)\b")
    replacements = {k: v for k, v in zip("01258", "OIZSB")}

    # Check to see if the provided system name follows the procedural format.
    matched = match_regex.match(system)
    if matched:
        sector = matched.group(1).strip()
        letters = f"{matched.group(2)} {matched.group(3)}"
        numbers = matched.group(4)

        for letter, number in replacements.items():
            letters = letters.replace(letter, number)
            numbers = numbers.replace(number, letter)

        # Re-format the string to ensure no extraneous spaces are included.
        return f"{sector} {letters}{numbers}"

    # Don't try and correct a system that isn't procedurally named.
    return system
