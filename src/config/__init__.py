"""
__init__.py -   Configuration plugin system.

This module houses the configuration plugin system, which enables arbitrary modules to plug into configuration related
events.


Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

Usage
----------------

    A plugin may be defined as either a class or a module namespace

    Within this namespace, you should define the two methods of the system.

    .. code::python
    >>> import typing
    >>> class MyPlugin:
    ...     @CONFIG_MARKER
    ...     def rehash_handler(self, data: typing.Dict):
    ...         ...
    ...
    ...     @CONFIG_MARKER
    ...     def validate_config(self, data: typing.Dict):
    ...         ...


    .. warning::
         an event hook can accept *less* arguments than the hook specification, but having more arguments than
         the specification allows results in an exception.

         This is a feature the underlying `pluggy` package provides.

    Once your plugin is defined, you need to register it against the :obj:`PLUGIN_MANAGER`.
    While not strictly required, you should give your plugin a unique name.

    .. code::
        >>> PLUGIN_MANAGER.register(MyPlugin(), "src.config.doctest_plugin")
        'src.config.doctest_plugin'


    .. hint::
        For module-scoped plugins it is recommended to use the containing package's `__init__.py` file to have this done
        automatically at load time

    See Also:
        `src.config <src >`_

hello world!
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
This decorator is used by plugins to signify which functions / methods of theirs to use as a configuration plugin 
handler.

.. warning:: If the handler is not marked using this decorator, it will **not** be recognized by the system.


"""

__all__ = ["CONFIG_MARKER", "PLUGIN_MANAGER", "setup"]
