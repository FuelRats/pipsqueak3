import logging
from uuid import UUID

import config
from ratlib.names import Platforms

LOG = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


class Rats(object):
    """
    This class keeps track of known rats as they are used and stores them in a
    class cache.

    Instances of this class are used to represent a unique, individual rat.

    Creation of a `Rats` object will automatically add the created rat to the
    cache, allowing convenience method `Rats.get_rat` to return the instance
    when called.
    """

    cache_by_id = {}
    """Cache of rat objects by their UUID"""
    cache_by_name = {}
    """Cache of rat objects by rat name (str)"""

    def __init__(self, uuid: UUID, name: str = None, platform: Platforms = Platforms.DEFAULT):
        """
        Creates a new rat

        Args:
            uuid (UUID):
            name (str): rat's name
            platform (Platforms): rat's platform
        """
        # set our properties
        self._platform = None
        self._uuid = uuid
        self._name = name
        # and update the cache
        if name:
            Rats.cache_by_name[name] = self
        Rats.cache_by_id[uuid] = self

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
            LOG.debug(f"value was a string with data '{value}'")
            uuid = UUID(value)
            LOG.debug("parsed value into a valid UUID.")
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
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, value):
        if isinstance(value, Platforms):
            self._platform = value
        else:
            raise TypeError(f"Expected a {Platforms} object, got type {type(value)}")

    @classmethod
    def get_rat(cls, name: str, platform: Platforms = Platforms.DEFAULT) -> 'Rats' or None:
        """
        Finds a rat either by name or by uuid.

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

        try:
            found = Rats.cache_by_name[name]
        except KeyError:
            # no such rat in cache
            return None
        else:
            # we found a rat
            if platform == Platforms.DEFAULT:
                # no platform check
                return found
            else:
                return found if found.platform == platform else None

    @classmethod
    def flush(cls) -> None:
        """
        Flushes the caches.

        Returns:
            None
        """
        cls.cache_by_id = {}
        cls.cache_by_name = {}
