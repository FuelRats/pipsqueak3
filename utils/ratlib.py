"""
ratlib.py - IRC/Fuelrat nickname utilities

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import re
import humanfriendly
import datetime
from datetime import timedelta
from enum import Enum
from math import isclose, sqrt
from uuid import UUID
from typing import Optional
from dataclasses import dataclass

STRIPPED_CHARS = '\t'


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


class Formatting(Enum):
    """
    mIRC-style formatting codes, works with colors
    """
    # this code needs to be suffixed to the colors above to actually display a color
    FORMAT_COLOR = '\x03'
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

    # Remove IRC control codes for color, bold, underline, etc.
    control_code_regex = re.compile(r"([\x02\x1D\x1F\x1E\x11\x16\x0F]|"
                                    r"(\x03([0-9]{1,2}(,[0-9]{1,2})?)?)|"
                                    r"(\x04([0-9a-fA-F]{6}(,[0-9a-fA-F]{6})?)?))"
                                    )
    sanitized_string = control_code_regex.sub('', sanitized_string)

    # Remove stripped characters. (e.g. Tabs)
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


# duration functions
def duration(time: datetime.timedelta) -> str:
    """
    Converts a timedelta into a more friendly human readable string, such as
    '5m 3w 4d ago'
    Args:
        time: (timedelta) time.

    Returns: (str) Easier-to-read time.

    """
    if not isinstance(time, datetime.timedelta):
        raise TypeError("ratlib.duration method requires a datetime or timedelta.")

    return humanfriendly.format_timespan(time, detailed=False, max_units=2)


def correct_system_name(system: str) -> str:
    """
    Take a system name and attempt to correct common mistakes to get the true system name.

    Args:
        system (str): The system name to check for corrections.

    Returns:
        The system name with any corrections applied, uppercased.
    """
    system = system.upper()
    match_regex = re.compile(r"(.*)\b([A-Z01258]{2}-[A-Z01258])\s+"
                             r"([A-Z01258])\s*([0-9OIZSB]+(-[0-9OIZSB]+)?)\b")
    replacements = {k: v for k, v in zip('01258', 'OIZSB')}

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


# color functions
def color(text: str, text_color: Colors, bg_color: Optional[Colors] = None) -> str:
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
        return f'{Formatting.FORMAT_COLOR.value}{text_color},{bg_color}{text}' \
               f'{Formatting.FORMAT_COLOR.value}'
    else:
        return f'{Formatting.FORMAT_COLOR.value}{text_color}{text}{Formatting.FORMAT_COLOR.value}'


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


@dataclass(frozen=True)
class Vector:
    """
    Represents a point within 3D space.
    """

    x: float
    y: float
    z: float

    def magnitude(self) -> float:
        """
        The magnitude of the vector, or the total distance between it and
        the origin (0, 0, 0).
        """

        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normal(self) -> 'Vector':
        """
        The normalized vector, representing 1 "unit" of distance in the Vector's
        original direction.

        Returns:
            The normalized vector, if valid.

        Raises:
            ValueError: If `magnitude()` is zero, the Vector must be (0, 0, 0), and therefore
                        has no normal.
        """

        mag = self.magnitude()
        if mag == 0:
            raise ValueError('Cannot normalize a zero Vector.')
        return Vector(self.x / mag, self.y / mag, self.z / mag)

    def distance(self, other) -> float:
        """
        Calculates the total distance between two Vectors.
        """

        return sqrt(
            ((other.x - self.x) ** 2) +
            ((other.y - self.y) ** 2) +
            ((other.z - self.z) ** 2))

    @classmethod
    def zero(cls) -> 'Vector':
        """
        Returns the zero Vector.
        """
        return cls(0, 0, 0)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __eq__(self, other):
        return (isclose(self.x, other.x) and
                isclose(self.y, other.y) and
                isclose(self.z, other.z))
