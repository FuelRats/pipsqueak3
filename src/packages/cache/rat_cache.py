"""
rat_cache.py - Caching facilities for Rat

Provides a caching facility for Rat, allowing created Rat to be reused without further API
Queries.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from typing import Dict, Optional, TYPE_CHECKING
from uuid import UUID

from src.packages.utils import Platforms, Singleton

if TYPE_CHECKING:
    from src.packages.rat.rat import Rat


class RatCache(Singleton):
    """
    A cache of rat objects
    """

    def __init__(self, api_handler=None):
        """
        Creates the ratcache
        """
        if not hasattr(self, "_initalized"):
            self._initalized = True
            self._cache_by_id: Dict[UUID, "Rat"] = {}
            self._cache_by_name: Dict[str, "Rat"] = {}
            self._api_handler = api_handler

    @property
    def api_handler(self):
        """
        RatCache's API handler
        """
        return self._api_handler

    @api_handler.setter
    def api_handler(self, value):
        self._api_handler = value
        # FIXME: add type check once the API gets merged in

    @property
    def by_uuid(self) -> Dict[UUID, "Rat"]:
        """
        Cache indexed by rat's UUID

        Returns:
            Dict[UUID, Rat]: ratcache indexed by UUID
        """
        return self._cache_by_id

    @by_uuid.setter
    def by_uuid(self, value: Dict[UUID, "Rat"]) -> None:
        """
        Sets the ratcache's by_uuid property

        Args:
            value (Dict[UUID, Rat]): new value for the cache

        Returns: None

        Raises:
            TypeError: illegal type.
        """
        if not isinstance(value, dict):
            raise TypeError(f"expected a dict. got {type(value)}")

        self._cache_by_id = value

    @property
    def by_name(self) -> Dict[str, "Rat"]:
        """
        Rats cache indexed by rat names

        Returns:
            Dict[str, Rat]
        """
        return self._cache_by_name

    @by_name.setter
    def by_name(self, value: Dict[str, "Rat"]) -> None:
        if not isinstance(value, Dict):
            raise TypeError(f"expected a dict, got {type(value)}")
        self._cache_by_name = value

    async def get_rat_by_name(self, name: str,
                              platform: Optional[Platforms] = None,
                              ) -> "Rat" or None:
        """
        Finds a rat by name and optionally by platform

        Will also accept both, and only return if the rat name matches its
        uuid entry.

        Args:
            name (str): name to search for
            platform (Platforms): platform to narrow search results by, if any.
                - defaults to any platform (first match)

        Returns:
            Rat - found rat
        """
        if not isinstance(name, str) or not isinstance(platform,
                                                       Platforms) and platform is not None:
            raise TypeError("invalid types given.")

        # initialize before use
        found = None

        try:
            found = self.by_name[name]
        except KeyError:
            # no such rat in cache
            if self.api_handler is not None:
                found = await self.api_handler.someApiCall(name=name)  # pragma: no cover
                # FIXME: replace SomeApiCall with the actual call once we have the interface
            return found
        else:
            # we found a rat
            return found if (found.platform == platform or platform is None) else None

    async def get_rat_by_uuid(self, uuid: UUID) -> Optional["Rat"]:
        """
        Finds a rat by their UUID.

        This method will first check the local cache and, in the event of a cache miss, will make an
            API call.

        Args:
            uuid (UUID): api uuid to find a rat for

        Returns:
            Rat: found rat
        """
        if not isinstance(uuid, UUID):
            raise TypeError
        else:
            found = None
            if uuid in self.by_uuid:
                found = self.by_uuid[uuid]
            elif self.api_handler is not None:  # pragma: no cover
                found = await self.api_handler.get_rat_by_id(id=uuid)

            return found

    def flush(self) -> None:
        """
        Flushes the caches.

        Returns:
            None
        """
        self.by_name.clear()
        self.by_uuid.clear()
