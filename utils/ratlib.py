"""
ratlib.py - IRC/Fuelrat nickname utilities

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import re
from enum import Enum
from uuid import UUID
from typing import Optional

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


class Status(Enum):
    """Rescue status enum"""
    OPEN = 0
    """The rescue is currently open"""
    CLOSED = 1
    """The rescue is currently closed"""
    INACTIVE = 2
    """The rescue is open, but is marked inactive"""


class Colors(Enum):
    """
    Contains mIRC-style color codes (the standard)
    Reference: https://www.mirc.com/colors.html
    """
    WHITE = '00'
    BLACK = '01'
    BLUE = '02'
    GREEN = '03'
    RED = '04'
    BROWN = '05'
    PURPLE = '06'
    ORANGE = '07'
    YELLOW = '08'
    LIGHT_GREEN = '09'
    CYAN = '10'
    LIGHT_CYAN = '11'
    LIGHT_BLUE = '12'
    PINK = '13'
    GREY = '14'
    LIGHT_GREY = '15'
    # this code needs to be suffixed to the colors above to actually display a color
    FORMAT_COLOR = '\x03'


class Formatting(Enum):
    """
    mIRC-style formatting codes, works with colors
    """
    FORMAT_BOLD = '\x02'
    FORMAT_UNDERLINE = '\x1F'
    FORMAT_ITALIC = '\x1D'
    FORMAT_REVERSE = '\x16'
    FORMAT_RESET = '\x0F'


class Singleton(object):
    """
    Provides a singleton base class.

    Any class derived from this base will be a singleton.

    Examples:
        >>> class Potato(Singleton):
        ...     pass
        >>> foo = Potato()
        >>> bar = Potato()
        >>> foo is bar
        True
    """

    def __new__(cls, *args, **kwargs):
        # checks if this class already has an instance.
        if cls._instance is None:
            # class does not already have an instance, lets make one!
            cls._instance = super().__new__(cls, *args, **kwargs)
        # return the instance
        return cls._instance

    def __init_subclass__(cls, **kwargs):

        # implements ._instance in all children
        cls._instance = None
        # and ensure the super gets called
        super().__init_subclass__(**kwargs)


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


def try_parse_uuid(suspect: str) -> UUID:
    result = None

    try:
        result = UUID(suspect, version=4)
    except ValueError:
        return None

    else:
        return result


# color functions
def color(text: str, text_color: Colors, bg_color=Optional[Colors]) -> str:
    """
    Colorizes the given string with the specified color.
    Args:
        text: The text to colorize
        text_color: a Colors.COLOR
        bg_color: if specified, the background color

    Returns:
        str: colorized string
    """
    if not isinstance(text_color, Colors):
        raise TypeError("Expected a Colors enum, got {type(text_color)}")
    if isinstance(bg_color, Colors):
        return f'{Colors.FORMAT_COLOR.value}{text_color},{bg_color}{text}' \
               f'{Colors.FORMAT_COLOR.value}'
    else:
        return f'{Colors.FORMAT_COLOR.value}{text_color}{text}{Colors.FORMAT_COLOR.value}'


def bold(text: str) -> str:
    """
    Makes the text bold.
    Args:
        text: The text.

    Returns:
        str: the bolded text

    """
    return f'{Formatting.FORMAT_BOLD.value}{text}{Formatting.FORMAT_BOLD.value}'


def italic(text: str) -> str:
    """
    Italicizes the given text.
    Args:
        text: the text

    Returns:
        str: the italicized text
    """
    return f'{Formatting.FORMAT_ITALIC.value}{text}{Formatting.FORMAT_ITALIC.value}'


def underline(text: str) -> str:
    """
    Underlines the given text.
    Args:
        text: the text

    Returns:
        str: the underlined text

    """
    return f'{Formatting.FORMAT_UNDERLINE.value}{text}{Formatting.FORMAT_UNDERLINE.value}'


def reverse(text: str) -> str:
    """
    Reverses the default colors (black on white text to white on black text)
    Args:
        text: the text to reverse

    Returns:
        str: the reversed text

    """
    return f'{Formatting.FORMAT_REVERSE.value}{text}{Formatting.FORMAT_REVERSE.value}'
