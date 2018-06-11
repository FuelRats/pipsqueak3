"""
ratlib.py - IRC/Fuelrat nickname utilities

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from enum import Enum
import re

MIRC_CONTROL_CODES = ["\x0F", "\x16", "\x1D", "\x1F", "\x02",
                      "\x03([1-9][0-6]?)?,?([1-9][0-6]?)?"]
STRIPPED_CHARS = ';\''


class Platforms(Enum):
    """
    Stores the different platforms we care about
    """
    PC = "PC"
    XB = "XB"
    PS = "PS"
    DEFAULT = None
    """No platform"""


class Status(Enum):
    """Rescue status enum"""
    OPEN = 0
    """The rescue is currently open"""
    CLOSED = 1
    """The rescue is currently closed"""
    INACTIVE = 2
    """The rescue is open, but is marked inactive"""


def sanitize(message: str) -> str:
    """
    Sanitizes and makes safe any text passed by removing mIRC Color,
    Bold, italic, and reverse flags.
    Removes semi-colons and tabs.

    Args:
        message (str): raw input message, from IRC.

    Returns:
        str: sanitized text string.
    """
    sanitized_string = message

    # Remove mIRC codes
    for code in MIRC_CONTROL_CODES:
        sanitized_string = re.sub(code, '', sanitized_string, re.UNICODE)

    # Remove tabs and semi-colons
    for character in sanitized_string:
        if character in STRIPPED_CHARS:
            sanitized_string = sanitized_string.replace(character, '')

    sanitized_string = ' '.join(sanitized_string.split())

    return sanitized_string


def strip_name(nickname: str) -> str:
    """
    This function accepts one input `nickname` and returns the input string
    minus any tags.

    An IRC tag is anything starting with "`[`". Further, anything following a
    `[` is truncated.

    Args:
        nickname (str): raw nickname to strip tags

    Returns:
        str: nickname stripped of tags
    """
    split_string = nickname.split("[")
    return split_string[0]
