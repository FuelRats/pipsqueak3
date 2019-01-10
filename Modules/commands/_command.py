"""
_command.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from asyncio import run
from collections import abc
from logging import getLogger
from typing import List, Callable, Optional, Any, Dict

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

    def __init__(self, *names,
                 underlying: Callable,
                 require_permission=False,
                 require_dm=False,
                 require_channel=False):

        assert names, "at least one name is required."

        self._aliases: List[str] = names
        self._setup_hooks: List[Callable] = []
        """
        pre-execution setup_hooks
        """

        self._teardown_hooks: List[Callable] = []
        """
        post-execution setup_hooks
        """

        self._underlying = underlying

        # sanity check
        if require_channel and require_dm:
            raise ValueError("require_dm and require_channel are mutually exclusive.")
        # hook registration checks
        if require_permission:
            LOG.debug(f"adding permission hook at level {require_permission} ...")
            self._setup_hooks.append(_hooks.require_permission)

        if require_dm:
            LOG.debug("enabling require direct message hook...")
            self._setup_hooks.append(_hooks.require_direct_message)

        if require_channel:
            LOG.debug("enabling require channel hook...")
            self._setup_hooks.append(_hooks.require_channel)

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
    def setup_hooks(self) -> List[Callable]:
        """
        List of pre-execution setup_hooks
        """
        return self._setup_hooks

    @property
    def teardown_hooks(self) -> List[Callable]:
        """
        List of post-execution hooks
        """
        return self._teardown_hooks

    @property
    def aliases(self) -> List[str]:
        """
        Lists of alias the underlying can be invoked by
        """
        return self._aliases

    async def setup(self, *args, **kwargs) -> List[Optional[Dict[str, Any]]]:
        """
        Executes setup setup_hooks, gathers the results

        Returns:
            list of kwarg dictionary objects, the results of each setup hook.
        """

        # build a list from the output of each setup task
        results = [await task(*args, **kwargs) for task in self._setup_hooks]
        return results

    async def teardown(self, *args, **kwargs):
        """
        Executes teardown tasks

        Yields:
            result of each teardown hook

        """
        for task in self.teardown_hooks:
            await task(*args, **kwargs)

    async def __call__(self, *args, **kwargs):
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
