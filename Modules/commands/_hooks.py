"""
_hooks.py - Core execution hooks implementation

provides the core implementation of execution hooks.

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
    """
    Base class for hook implementations.

    Any useful child implementation should implement either `pre_execute` or `post_execute` but it
    is not required.

    It is also recommended subclasses implement a repr method.

    Notes:
        objects derived this base cannot be dynamically assigned to, this is by design.
    """
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
    """
    Pre-execution methods can raise this to stop the execution, this will cause the underlying
    to **not** be called, and any previously run hooks to have their teardowns called.
    """

    def __call__(self, context: Context):
        # call our setup routine
        yield self.pre_execute(context)
        # call our teardown routine
        return self.post_execute(context)


# module attribute
hooks: Dict[str, type(HookImplementation)] = {}
"""
All known event hooks.
"""


def hook(name: str):
    """
    Registers the decorated class as a Command hook.

    Args:
        name (str): name to use as the keyword argument to enable this hook

    once registered, it can be "enabled" for any command registration simply by passing a value
    to `name` as a keyword argument.

    See Also
        :class:`Modules.commands.Registry`
    Returns:
        cls unchanged.
    """
    def real_decorator(cls):
        assert issubclass(cls, HookImplementation)
        hooks[name] = cls
        return cls

    return real_decorator


