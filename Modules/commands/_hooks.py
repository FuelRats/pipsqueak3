"""
_hooks.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from collections.abc import Callable
from logging import getLogger
from typing import AsyncGenerator

from Modules.context import Context

LOG = getLogger(f"mecha.{__name__}")

class CancelExecution(Exception):
    """
    Raised when a setup hook wants to cancel execution

    **note** This should __only__ be raised by pre-execution hooks!
    """
    ...


# #######
# pre-execute hooks
# #

async def require_channel(context: Context, *args, **kwargs):
    LOG.debug("in require_channel")
    if not context.channel:
        await context.reply("this callable must be invoked in a channel")
        raise CancelExecution("this callable must be invoked in a channel")


async def require_direct_message(context: Context, *args, **kwargs):
    LOG.debug("in require_direct_message")

    if context.channel:
        await context.reply("this callable must be invoked from a direct message with me.")
        raise CancelExecution("this callable must be invoked from a direct message with me.")

# #######
# post-execute hooks
# #
