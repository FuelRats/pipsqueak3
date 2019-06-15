"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from .board import RatBoard
from . import board as _board

from src.config import PLUGIN_MANAGER

PLUGIN_MANAGER.register(_board, "Rat Board")
__all__ = [
    "RatBoard",

]
