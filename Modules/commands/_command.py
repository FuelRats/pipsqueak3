"""
_command.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from collections import abc
from logging import getLogger
from typing import List, Callable, Optional, Any, Dict

from Modules.context import Context
from . import _hooks

LOG = getLogger(f"mecha.{__name__}")


class Command(abc.Callable, abc.Container):
    """
    Defines a Command.

    Examples:
        This class implements :class:`abc.Container`, using string aliases for the contains check.
        >>> async def foo(*args, **kwargs):
        ...     print("foo called!")
        >>> cmd = Command('doc_command_foo', underlying=foo)

        >>> 'doc_command_foo' in cmd
        True

        This class is also :class:`abc.Callable`, thus can be called directly
        >>> run(cmd())
        foo called!
    """
    __slots__ = ['_underlying',
                 '_hooks'
                 ]

    def __init__(self, *names,
                 underlying: Callable,
                 **kwargs):

        if not names:
            raise ValueError("at least one name is required.")
        self._hooks: List = []  # todo proper type hint

        # for each kwarg
        for key, value in kwargs.items():
            # match it to its corresponding hook
            hook = _hooks.hooks[key](value)
            self._hooks.append(hook)

        self._aliases: List[str] = names

        self._underlying = underlying

    def __contains__(self, item: str):
        # check if its a string
        if not isinstance(item, str):
            # its not, bailout
            return NotImplemented
        # check if the specified item is one of ours
        return item in self.aliases

    @property
    def name(self):
        """
        return the first alias this command is known by, aka its name
        """
        return self.aliases[0]

    @property
    def underlying(self) -> Callable:
        """
        The underlying command function, with no setup_hooks applied.
        """
        return self._underlying

    @property
    def aliases(self) -> List[str]:
        """
        Lists of alias the underlying can be invoked by
        """
        return self._aliases

    async def __call__(self, context:Context):
        """
        Invoke this command.

        First thing this function does is call the setup hooks, allowing for pre-command execution
        behavior.
        If any of the setup hooks return :obj:`_hooks.STOP_EXECUTION` then execution will be
        canceled.

        Any uncalled setup hooks are discarded, and the underlying / teardown hooks are
        also discarded.

        Args:
            *args: Positional arguments to pass to hooks and underlying
            **kwargs (): Keyword arguments to pass to hooks and underlying
        """

        LOG.debug(f"command {self.aliases[0]} invoked...")

        try:
            # extra arguments to pass to the underlying
            extra_arguments = {}

            hook_gens = (hook(context) for hook in self._hooks)

            # if we have setup tasks to do
            if self.setup_hooks:
                # Invoke the setup tasks and filter out the no-returns
                results = [result for result in await self.setup(*args, **kwargs) if
                           result is not None]
                LOG.debug(f"processing results list {results}...")
                for item in results:
                    extra_arguments.update(item)

                LOG.debug(f"done parsing results list. final dict to be unpacked into underlying:"
                          f"{extra_arguments}")
            else:
                LOG.debug(f"<{self.name}>:no setup hooks for command, skipping...")
        except _hooks.CancelExecution:
            # check if the hook wants to stop the execution
            LOG.debug(f"<{self.name}>: setup hook canceled execution.")

        else:
            # no setup errors, no setup cancels. invoke the underlying.
            LOG.debug(f"<{self.name}>:invoking the underlying...")
            # all is good, invoke the underlying
            await self.underlying(*args, **kwargs, **extra_arguments)

            # finally execute teardown tasks some teardown

        finally:
            # always call teardown
            if self.teardown_hooks:
                LOG.debug(f"<{self.name}>:executing teardown tasks for command...")
                await self.teardown(*args, **kwargs)

            else:
                LOG.debug(f"<{self.name}>:no teardown hooks for command.")
