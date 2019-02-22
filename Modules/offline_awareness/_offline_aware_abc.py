"""
_offline_aware_abc.py - Provides an offline awareness ABC

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging
import weakref
from abc import abstractmethod, ABC
from typing import List, NoReturn

LOG = logging.getLogger(f"mecha.{__name__}")


class OfflineAwareABC(ABC):
    """
    Interface for offline-aware classes
    """
    __slots__ = []
    _storage: List[weakref.finalize] = []
    """
    Private weak reference storage
    """

    online = False
    """
    Are we in online mode?
    """

    def __init__(self):
        """
        registers the subclass obj instance weakly. used for event propagation
        """

        # create a finalizer-based weak reference, tie the callback to our GC method
        # then append it to our storage object
        self._storage.append(weakref.finalize(self, self.__gc))

    @abstractmethod
    async def on_online(self) -> NoReturn:
        """
        on_online event callback, invoked  when the system moves to "online" mode
        """

    @abstractmethod
    async def on_offline(self) -> NoReturn:
        """
        on_offline event callback, invoked when the system moves to "offline" mode
        """

    @classmethod
    async def go_online(cls) -> NoReturn:
        """
        Moves the system to "online" mode

        Notes
            This function is Idempotent.
        """
        if cls.online:
            return  # already online, bail out.

        cls.online = True
        for reference in cls._storage:
            # check if its still alive (possible to expire during iteration)
            if reference.alive:
                # resolve the reference
                strong_reference = reference.peek()[0]

                # and invoke its callback
                await strong_reference.on_online()

    @classmethod
    async def go_offline(cls):
        """
        Moves the system to "Offline" mode.

        Notes:
            This function is Idempotent.
        """
        if not cls.online:
            return  # already offline, bail out.

        cls.online = False

        for reference in cls._storage:
            # check if its still alive (possible to expire during iteration)
            if reference.alive:
                # resolve the reference
                strong_reference = reference.peek()[0]

                # and invoke its callback
                await strong_reference.on_offline()

    @classmethod
    def __gc(cls) -> int:
        """
        Garbage collect dead references. called when a weak reference dies.

        Returns:
            number of references collected
        """
        LOG.debug(f"garbage collection invoked...")

        # calculate which references are dead
        to_delete = {reference for reference in cls._storage if not reference.alive}

        culled = len(to_delete)
        # and cull them
        for reference in to_delete:
            cls._storage.remove(reference)

        LOG.debug(f"garbage collection complete. {culled} dead references culled")
        return culled
