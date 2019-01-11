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


class HookImplementation:
    __slots__ = ['__weakref__']  # disallow dynamic attribute creation (__dict__)

    def __repr__(self):
        return f"HookImplementation()"

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


# module attribute
hooks: Dict[str, type(HookImplementation)] = {}


def hook(name: str):
    def real_decorator(cls):
        assert issubclass(cls, HookImplementation)
        hooks[name] = cls
        return cls

    return real_decorator


@hook("require_channel")
class RequireChannelHook(HookImplementation):
    """
    Require Channel hook implementation
    """
    __slots__ = ['message']

    def __init__(self, message="this MUST be executed in a channel"):
        self.message = message

    def __repr__(self):
        return f"RequireChannelHook(message='{self.message}')"

    async def pre_execute(self, context: Context):
        LOG.debug("in require_channel")
        if not context.channel:
            await context.reply(self.message)
            raise self.Cancel(self.message)


@hook("require_dm")
class RequireDirectMessageHook(HookImplementation):
    __slots__ = ['message']

    def __init__(self, message="this MUST be executed from a direct message with me!"):
        self.message = message

    def __repr__(self):
        return f"RequireDirectMessageHook(message='{self.message}')"

    async def pre_execute(self, context: Context):
        LOG.debug("in RequireDirectMessage setup...")
        if context.channel:
            await context.reply(self.message)
            raise self.Cancel(self.message)


