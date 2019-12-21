"""
rat.py - Rat object

Handles the rats cache and provides facilities for managing rats.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""

from functools import reduce
from operator import xor
from typing import Optional
from uuid import UUID

from loguru import logger

from ..utils import Platforms


class Rat:
    """
    This class keeps track of known rats as they are used and stores them in a
    class cache.

    Instances of this class are used to represent a unique, individual rat.

    Creation of a `Rat` object will automatically add the created rat to the
    cache.
    """

    def __init__(self, uuid: UUID, name: str = None, platform: Optional[Platforms] = None):
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

    def __eq__(self, other: 'Rat') -> bool:
        """
        Compare two Rats objects for equality

        Args:
            other (Rat): other object to compare

        Returns:
            bool: equal if uuid, platform, and name match
            NotImplemented: bad type given
        """

        if not isinstance(other, Rat):
            return NotImplemented
        return (self.platform, self.uuid, self.name) == (other.platform, other.uuid, other.name)

    def __hash__(self) -> int:
        if self._hash is None:
            attrs = (self.platform, self.uuid, self.uuid, self.name)
            self._hash = reduce(xor, map(hash, attrs))

        return self._hash

    @property
    def unidentified(self):
        """ Returns if this Rat object is identified (bound to an API identity) """
        return self.uuid is None

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
            logger.debug(f"Value was a string with data '{value}'")
            uuid = UUID(value)
            logger.debug("Parsed value into a valid UUID.")
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
        The Rat platform

        Returns:
            Platforms: The platform the rat is registered on
        """
        return self._platform

    @platform.setter
    def platform(self, value: Optional[Platforms]) -> None:
        """
        Sets the platform for a given rat

        Args:
            value (Platforms): new platform
        """
        if isinstance(value, Platforms) or value is None:
            self._platform = value
        else:
            raise TypeError(f"Expected a {Platforms} object, got type {type(value)}")
