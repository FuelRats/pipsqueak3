"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from Modules.commands import command_registry
from Modules.permissions import RAT
from Modules.context import Context

__all__ = []

if __debug__:
    from . import debug

    __all__.append('debug')


@command_registry.register("ping", require_permission=RAT)
async def cmd_ping(context: Context):
    await context.reply("Pong!")
