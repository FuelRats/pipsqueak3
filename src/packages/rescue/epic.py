"""
epic.py - Epic data structure

Provides an Epic object for storing Epic data from the API

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

"""
from functools import reduce
from operator import xor
from typing import Optional
from uuid import UUID

from src.packages.rat.rat import Rat


class Epic(object):
    """
    Epic rescue data
    """

    def __init__(self,
                 uuid: UUID,
                 notes: str,
                 rescue: Optional['Rescue'] = None,
                 rat: Optional[Rat] = None):
        """
        Creates a new Epic object.

        Epics can only have one associated rat and Rescue

        Args:
            uuid (UUID): api id of Epic
            notes (str): Epic's notes
            rescue (Rescue): Associated Rescue
            rat (Rat):    Associated rat rats
        """
        self._hash: Optional[int] = None
        self._uuid: uuid = uuid
        self._notes: str = notes
        self._rescue: 'Rescue' = rescue
        self._rat: Rat = rat

    @property
    def uuid(self) -> UUID:
        """
        API id of the epic

        Returns:
            UUID: API ID
        """
        return self._uuid

    @property
    def notes(self) -> str:
        """
        associated epic notes

        Returns:
            str
        """
        return self._notes

    @property
    def rescue(self) -> 'Rescue':
        """
        Associated epic rescue

        Returns:
            Rescue: epic rescue object
        """
        return self._rescue

    @property
    def rat(self) -> Rat:
        """
        Rat associated with Epic rescue

        Returns:
            rats
        """
        return self._rat

    def __eq__(self, other: 'Epic') -> bool:
        # type and null check
        if not isinstance(other, Epic):
            return NotImplemented

        attributes = (self.rescue == other.rescue,
                      self.uuid == other.uuid,
                      self.notes == other.notes,
                      self.rat == other.rat)
        return all(attributes)

    def __hash__(self) -> int:
        if self._hash is None:
            attrs = (self.rescue, self.uuid, self.notes, self.rat)
            self._hash = reduce(xor, map(hash, attrs))

        return self._hash
