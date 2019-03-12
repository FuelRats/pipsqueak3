"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from .autocorrect import correct_system_name
from .ratlib import sanitize, Vector, Colors, color, bold, underline, italic, reverse, Platforms, \
    Singleton, Status, Formatting

__all__ = [
    "autocorrect",
    "ratlib",
    "Vector",
    "Colors",
    "color",
    "bold",
    "underline",
    "italic",
    "reverse",
    "sanitize",
    "Platforms",
    "Formatting"
]
