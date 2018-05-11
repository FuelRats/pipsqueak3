"""
names.py - IRC/Fuelrat nickname utilities

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from enum import Enum


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

