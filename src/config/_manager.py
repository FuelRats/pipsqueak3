"""
$file.fileName - $shortDescripion  # FIXME template

$longDescription
Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

#
#  Copyright (c) $DateInfo.year The Fuel Rats Mischief,
#  All rights reserved.
#
#  Licensed under the BSD 3-Clause License.
#
#  See LICENSE.md
#

import logging

import pluggy

from ._constants import _PLUGIN_NAME

LOG = logging.getLogger(f"mecha.{__name__}")
plugin_manager = pluggy.PluginManager(_PLUGIN_NAME)
