"""
__init__.py -   # FIXME teplates



Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import pluggy

# the specifications
from . import _spec
# and the constant(s)
from ._constants import _PLUGIN_NAME
# load our hook specification
from ._manager import PLUGIN_MANAGER
# load the parsers
from ._parser import load_config, setup_logging, setup

# create the plugin manager

# register our specifications
PLUGIN_MANAGER.add_hookspecs(_spec)

# create implementation markers

CONFIG_MARKER = pluggy.HookimplMarker(_PLUGIN_NAME)
"""
used to mark config plugin implementations
"""

__all__ = ["CONFIG_MARKER", "PLUGIN_MANAGER", "setup"]
