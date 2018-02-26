"""
names.py - IRC/Fuelrat nickname utilities

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""


def strip_name(nickname: str) -> str:
    """
    This function accepts one input `nickname` and returns the input string minus any tags.

    An IRC tag is anything starting with "`[`", and it is assumed anything after a tag is also a tag.

    Args:
        nickname (str): raw nickname to strip tags

    Returns:
        str: nickname stripped of tags
    """
    split_string = nickname.split("[")
    return split_string[0]

