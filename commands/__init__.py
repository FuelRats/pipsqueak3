"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from Modules.commands import command_registry
from Modules.context import Context
from Modules.permissions import RAT

__all__ = []

if __debug__:  # if the debug flag is set (not running optimized) import the debugging module
    from . import debug

    __all__.append('debug')


@command_registry.register("ping", require_permission=RAT)
async def cmd_ping(context: Context):
    await context.reply("Pong!")
