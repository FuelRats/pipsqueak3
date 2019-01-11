"""
_hooks.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from logging import getLogger
from typing import AsyncGenerator, Optional, Dict, Any, NoReturn

from Modules.context import Context

LOG = getLogger(f"mecha.{__name__}")

class CancelExecution(Exception):
    """
    Raised when a setup hook wants to cancel execution

    **note** This should __only__ be raised by pre-execution hooks!
    """
    ...


class HookImplementation:
    __slots__ = ['__weakref__']  # disallow dynamic attribute creation (__dict__)

    async def pre_execute(self, context: Context) -> Optional[Dict[str, Any]]:
        """
        Pre-execution Hook method. Anything you want to execute prior to running
        the underlying goes in here.

        To cancel the execution of underlying simply raise self.cancel(reason).

        Args:
            context (Context): Execution context

        Returns:
            Optional[Dict]: keyword arguments to pass to underling executable
        """
        ...

    async def post_execute(self, context: Context) -> NoReturn:
        """
        Teardown tasks to execute.

        This routine will be called even if the underlying was canceled by a setup routine.

        Args:
            context (Context): execution Cotnext
        """
        ...

    Cancel = CancelExecution  # convenience alias

    async def __call__(self, context: Context) -> AsyncGenerator:
        # call our setup routine
        yield await self.pre_execute(context)
        await self.post_execute(context)


class RequireChannelHook(HookImplementation):
    """
    Require Channel hook implementation
    """
    __slots__ = ['message']

    def __init__(self, message="this MUST be executed in a channel"):
        self.message = message

    async def pre_execute(self, context: Context):
        LOG.debug("in require_channel")
        if not context.channel:
            await context.reply(self.message)
            raise self.Cancel(self.message)


class RequireDirectMessageHook(HookImplementation):
    __slots__ = ['message']

    def __init__(self, message="this MUST be executed from a direct message with me!"):
        self.message = message

    async def pre_execute(self, context: Context):
        LOG.debug("in RequireDirectMessage setup...")
        if context.channel:
            await context.reply(self.message)
            raise self.Cancel(self.message)


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
