"""
__init__.py -   # FIXME teplates



Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import pluggy

# load our hook specification
from ._constants import _PLUGIN_NAME
from . import _spec

# create the plugin manager
plugin_manager = pluggy.PluginManager(_PLUGIN_NAME)

# register our specifications
plugin_manager.add_hookspecs(_spec)

# create implementation markers

implementation_marker = pluggy.HookimplMarker(_PLUGIN_NAME)

__all__ = ["plugin_manager", "implementation_marker"]
