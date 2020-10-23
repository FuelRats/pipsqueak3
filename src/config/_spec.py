"""
_spec.py  - Configuration plugin hook specifications

this file contains the hook specifications for the configuration system.
Any plugin implementing the configuration interface **must** implement the below
functions in order to benefit from the system.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import typing

import pluggy

from ._constants import _PLUGIN_NAME
from .datamodel import ConfigRoot

VALIDATOR_SPEC = pluggy.HookspecMarker(_PLUGIN_NAME)
REHASH_SPEC = pluggy.HookspecMarker(_PLUGIN_NAME)


# noinspection PyUnusedLocal
@VALIDATOR_SPEC
def validate_config(data: typing.Dict):  # pylint: disable=unused-argument
    """
    Validate new configuration data.

    Args:
        data (typing.Dict): new configuration data  to validate

    Raises:
        ValueError:  config section failed to validate.
        KeyError:  config section failed to validate.
    """


# noinspection PyUnusedLocal
@REHASH_SPEC
def rehash_handler(data: ConfigRoot):  # pylint: disable=unused-argument
    """
    Apply new configuration data

    Args:
        data (ConfigRoot): new configuration data to apply.

    """
