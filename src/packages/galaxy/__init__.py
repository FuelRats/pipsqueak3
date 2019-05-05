"""
__init__.py - Provide functionality and integration with the Fuel Rats Systems API.

This module provides several helpful functions to integrate with the Systems API
and provide useful information about the Elite: Dangerous galaxy.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from src.config import PLUGIN_MANAGER
from .galaxy import Galaxy
from .star_system import StarSystem

__all__ = ["Galaxy", "StarSystem"]

PLUGIN_MANAGER.register(Galaxy, "galaxy")
