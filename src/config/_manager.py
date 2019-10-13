"""
_manager.py  Configuration related plugin management

contains the configuration plugin manager

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging

import pluggy

from ._constants import _PLUGIN_NAME

PLUGIN_MANAGER = pluggy.PluginManager(_PLUGIN_NAME)
"""
Configuration plugin manager
"""
