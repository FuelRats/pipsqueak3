"""
rats.py - Rats object

Handles the rats cache and provides facilities for managing rats.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""

import logging
from functools import reduce
from operator import xor
from uuid import UUID

from config import config
from ratlib.names import Platforms

log = logging.getLogger(f"mecha.{__name__}")


class Rats(object):
    """
    This class keeps track of known rats as they are used and stores them in a
    class cache.

    Instances of this class are used to represent a unique, individual rat.

    Creation of a `Rats` object will automatically add the created rat to the
    cache, allowing convenience method `Rats.get_rat_by_name` to return the instance
    when called.
    """

    cache_by_id = {}
    """Cache of rat objects by their UUID"""
    cache_by_name = {}
    """Cache of rat objects by rat name (str)"""
    api_handler = None
    """API handler"""

    def __init__(self, uuid: UUID, name: str = None, platform: Platforms = Platforms.DEFAULT):
        """
        Creates a new rat

        Args:
            uuid (UUID):
            name (str): rat's name
            platform (Platforms): rat's platform
        """
        # set our properties
        self._platform = platform
        self._uuid = uuid
        self._name = name
        self._hash = None
        # and update the cache
        if name and name not in Rats.cache_by_name:
            # don't register duplicates
            Rats.cache_by_name[name] = self
        if uuid not in Rats.cache_by_id:
            # don't register duplicates
            Rats.cache_by_id[uuid] = self

    def __eq__(self, other: 'Rats')->bool:
        """
        Compare two Rats objects for equality

        Args:
            other (Rats): other object to compare

        Returns:
            bool: equal if uuid, platform, and name match

        Raises:
            TypeError : invalid type for equality check.
        """
        if other is None:
            return False

        if not isinstance(other, Rats):
            raise TypeError

        conditions = {
            self.platform == other.platform,
            self.uuid == other.uuid,
            self.name == other.name
        }
        return all(conditions)

    def __hash__(self) -> int:
        if self._hash is None:
            attrs = (self.platform, self.uuid, self.uuid, self.name)
            self._hash = reduce(xor, map(hash, attrs))

        return self._hash

    @property
    def uuid(self):
        """
        API id of the rat

        Returns:
            UUID
        """
        return self._uuid

    @uuid.setter
    def uuid(self, value) -> None:
        """
        Set the UUID of the rat.
        accepts a uuid encoded string, or a uuid object.

        Args:
            value (UUID): new uuid for rat

        Returns:
            None
        """
        if isinstance(value, str):
            log.debug(f"Value was a string with data '{value}'")
            uuid = UUID(value)
            log.debug("Parsed value into a valid UUID.")
            self._uuid = uuid
        elif isinstance(value, UUID):
            self._uuid = value

        else:
            raise TypeError(f"expected type None or type str, got "
                            f"{type(value)}")

    @property
    def name(self) -> str:
        """
        Rat's registered name

        Returns:
            str
        """
        return self._name

    @name.setter
    def name(self, value) -> None:
        """
        Sets the rat's registered name

        Args:
            value (str): name

        Returns:
            None
        """
        if isinstance(value, str):
            self._name = value
        else:
            raise TypeError(f"expected str, got {type(value)}")

    @property
    def platform(self) -> Platforms:
        """
        The Rats platform

        Returns:
            Platforms: The platform the rat is registered on
        """
        return self._platform

    @platform.setter
    def platform(self, value: Platforms) -> None:
        """
        Sets the platform for a given rat

        Args:
            value (Platforms): new platform
        """
        if isinstance(value, Platforms):
            self._platform = value
        else:
            raise TypeError(f"Expected a {Platforms} object, got type {type(value)}")

    @classmethod
    async def get_rat_by_name(cls, name: str,
                              platform: Platforms = Platforms.DEFAULT,
                              ) -> 'Rats' or None:
        """
        Finds a rat by name and optionally by platform

        Will also accept both, and only return if the rat name matches its
        uuid entry.

        Args:
            name (str): name to search for
            platform (Platforms): platform to narrow search results by, if any.
                - defaults to any platform (first match)

        Returns:
            Rats - found rat
        """
        if not isinstance(name, str) or not isinstance(platform, Platforms):
            raise TypeError("invalid types given.")

        # initialize before use
        found = None

        try:
            found = Rats.cache_by_name[name]
        except KeyError:
            # no such rat in cache
            if cls.api_handler is not None:
                found = await cls.api_handler.someApiCall(name=name)  # pragma: no cover
                # FIXME: replace SomeApiCall with the actual call once we have the interface
            return found
        else:
            # we found a rat
            return found if (found.platform == platform or platform == Platforms.DEFAULT) else None

    @classmethod
    async def get_rat_by_uuid(cls, uuid: UUID) -> 'Rats' or None:
        """
        Finds a rat by their UUID.

        This method will first check the local cache and, in the event of a cache miss, will make an
            API call.

        Args:
            uuid (UUID): api uuid to find a rat for

        Returns:
            Rats: found Rescue
        """
        if not isinstance(uuid, UUID):
            raise TypeError
        else:
            found = None
            if uuid in cls.cache_by_id:
                found = cls.cache_by_id[uuid]
            elif cls.api_handler is not None:  # pragma: no cover
                found = await cls.api_handler.get_rat_by_id(id=uuid)

            return found

    @classmethod
    def flush(cls) -> None:
        """
        Flushes the caches.

        Returns:
            None
        """
        cls.cache_by_id = {}
        cls.cache_by_name = {}
