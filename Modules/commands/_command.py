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
from typing import List, Callable

from . import _hooks

LOG = getLogger(f"mecha.{__name__}")


class Command:
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

        # hook registration checks
        if require_permission:
            self._setup_hooks.append(_hooks.require_permission)

        if require_dm:
            assert not require_channel, "require_dm and require_channel are mutually exclusive."
            self._setup_hooks.append(_hooks.require_direct_message)

        if require_channel:
            assert not require_dm, "require_dm and require_channel are mutually exclusive."
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

    async def setup(self, *args, **kwargs):
        """
        Executes setup setup_hooks,

        Yields:
            result of each setup task
        """
        for task in self.setup_hooks:
            yield await task(*args, **kwargs)

    async def teardown(self, *args, **kwargs):
        """
        Executes teardown tasks

        Yields:
            result of each teardown hook

        """
        for task in self.teardown_hooks:
            yield await task(*args, **kwargs)

    async def __call__(self, *args, **kwargs):
        """
        Invoke this command.


        Args:
            *args ():
            **kwargs ():

        Returns:

        """

        LOG.debug(f"command {self.aliases[0]} invoked...")
        # call setup tasks sequentially

        if self.setup_hooks:
            async for result in self.setup(*args, **kwargs):
                LOG.debug(f"<{self.name}>:result of setup hook:= {result}")
                # check if the hook wants to stop the execution
                if result is _hooks.STOP_EXECUTION:
                    LOG.debug(f"<{self.name}>:Setup hook terminated execution for command")
                    return
        else:
            LOG.debug(f"<{self.name}>:no setup hooks for command, skipping...")

        LOG.debug(f"<{self.name}>:invoking the underlying...")
        # all is good, invoke the underlying
        await self.underlying(*args, **kwargs)

        # finally execute teardown tasks some teardown

        if self.teardown_hooks:
            LOG.debug(f"<{self.name}>:executing teardown tasks for command")
            async for task_result in self.teardown(*args, **kwargs):
                LOG.debug(f"<{self.name}>: result of teardown hook: {task_result}")
        else:
            LOG.debug(f"<{self.name}>:no teardown hooks for command.")
