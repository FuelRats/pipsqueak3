"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from .board import RatBoard
from .rat_board import IndexNotFreeError, RescueBoardException, \
    RescueNotChangedException, RescueNotFoundException

__all__ = [
    "RatBoard",
    "RescueNotFoundException",
    "RescueNotChangedException",
    "IndexNotFreeError",
    "RescueBoardException"
]
