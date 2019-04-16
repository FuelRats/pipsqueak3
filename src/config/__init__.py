"""
__init__.py -   # FIXME teplates



Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import pluggy

from ._manager import plugin_manager
from ._parser import load_config, setup_logging, setup
from . import _spec
from ._constants import _PLUGIN_NAME
# load our hook specification
from ._manager import plugin_manager

# create the plugin manager
"""
Configuration plugin manager
"""

# register our specifications
plugin_manager.add_hookspecs(_spec)

# create implementation markers

config_marker = pluggy.HookimplMarker(_PLUGIN_NAME)
"""
used to mark config plugin implementations
"""

__all__ = ["config_marker", "plugin_manager", "setup"]
