"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
__all__ = [
    "Permission",
    "require_dm",
    "require_channel",
    "require_permission",
    "RAT",
    "TECHRAT",
    "RECRUIT",
    "OVERSEER",
    "ADMIN",
]
from src.config import PLUGIN_MANAGER
from .permissions import Permission, require_permission, require_dm, require_channel, RAT, \
    TECHRAT, RECRUIT, OVERSEER, ADMIN
from . import permissions

PLUGIN_MANAGER.register(permissions)
