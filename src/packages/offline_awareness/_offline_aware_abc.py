"""
_offline_aware_abc.py - Provides an offline awareness ABC

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import asyncio
import logging
import weakref
from abc import abstractmethod, ABC
from typing import Dict, List, NoReturn

from src.config import CONFIG_MARKER

LOG = logging.getLogger(f"mecha.{__name__}")


class OfflineAwareABC(ABC):
    """
    Interface for offline-aware classes

    Subclasses of this ABC will be notified when the system moves between online and offline modes

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

    @classmethod
    @CONFIG_MARKER
    def rehash_handler(cls, data: Dict):
        """
        Apply new configuration data

        Args:
            data (Dict): New configuration data to apply.
        """
        online = data['api']['online_mode']
        if online:
            method = cls.go_online
        else:
            method = cls.go_offline
        loop = asyncio.get_event_loop()
        loop.run_until_complete(method())

    @classmethod
    @CONFIG_MARKER
    def validate_config(cls, data: Dict):
        """
        Validate the configuration for Offline Awareness.

        Args:
            data (Dict): Configuration object.

        Raises:
            ValueError if the config fails validation.
        """
        if not isinstance(data['api']['online_mode'], bool):
            raise ValueError("[OfflineAware] Config option 'api.online_mode' must be a boolean.")

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
            LOG.debug("already in online mode, ignoring call to go_online ...")
            return  # already online, bail out.

        LOG.info("Moving to online mode...")
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
            LOG.debug("already in offline mode, ignoring call to go_offline ...")
            return  # already offline, bail out.
        LOG.info("Moving to offline mode")
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
