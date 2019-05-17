"""
$file.fileName - 


Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from __future__ import annotations

import itertools
import logging
import typing
from collections import abc
from contextlib import asynccontextmanager
from uuid import UUID

from src.packages.rescue import Rescue

CYCLE_AT = 15
"""
Determines at what board index does mecha (attempt) to start over indexing

Notes:
    mecha will still count beyond this value unrestricted, but will attempt
    to keep assigned case numbers below this value whenever possible.
"""
_KEY_TYPE = typing.Union[str, int, UUID]

LOG = logging.getLogger(f"mecha.{__name__}")


class RatBoard(abc.Mapping):
    """
    The Rat Board
    """
    __slots__ = ["_storage_by_uuid",
                 "_storage_by_client",
                 "_handler",
                 "_storage_by_index",
                 "_index_counter"]

    def __init__(self, api_handler=None):
        self._handler = api_handler
        """
        fuelrats.com API handler
        """
        self._storage_by_uuid: typing.Dict[UUID, Rescue] = {}
        """
        internal rescue storage keyed by uuid
        """
        self._storage_by_client: typing.Dict[str, Rescue] = {}
        """
        internal rescue storage keyed by client
        """
        self._storage_by_index: typing.Dict[int, Rescue] = {}
        """
        internal rescue storage keyed by board index
        """
        self._index_counter = itertools.count()
        """
        Internal counter for tracking used indexes
        """

    def __getitem__(self, key: _KEY_TYPE) -> Rescue:
        if isinstance(key, str):
            return self._storage_by_client[key]

        if isinstance(key, UUID):
            return self._storage_by_uuid[key]

        if isinstance(key, int):
            return self._storage_by_index[key]

        # not one of our key types,
        return super(RatBoard, self).__getitem__(key)

    def __len__(self) -> int:
        return len(self._storage_by_uuid)

    def __iter__(self) -> typing.Iterator[UUID]:
        return iter(self._storage_by_uuid)

    @property
    def _free_case_number(self) -> int:
        """
        returns the next unused index in the series.

        Returns:
            int: next free board index
        """
        # this line is so magical it gets its own method.
        # basically, this returns the next index from self._index_counter'
        # that is not already in use (contains & filterfalse)
        return next(itertools.filterfalse(self.__contains__, self._index_counter))

    @property
    def free_case_number(self) -> int:
        """
        Returns a unused case number

        Returns:
            int: unused case number

        Notes:
            This method will attempt to return values smaller than the defined
            :obj:`CYCLE_AT` whenever possible, though will return values
            in excess of :obj:`CYCLE_AT` as necessary.
        """
        next_free = self._free_case_number

        # if we are larger or equal to the CYCLE_AT point, reset the counter
        overflow = next_free >= CYCLE_AT
        if overflow:
            self._index_counter = itertools.count()
            # get the next free index from the underlying magic
            return self._free_case_number

        # return the next index from the magic
        return next_free

    def __contains__(self, key: _KEY_TYPE) -> bool:
        return (key in self._storage_by_client or
                key in self._storage_by_uuid or
                key in self._storage_by_index
                )

    def __delitem__(self, key: _KEY_TYPE):
        # get the target
        target = self[key]

        # and purge it key by key
        del self._storage_by_uuid[target.api_id]
        del self._storage_by_index[target.board_index]
        if target.client:
            del self._storage_by_client[target.client]

    @asynccontextmanager
    async def create_rescue(self, *args, ovewrite=False, **kwargs) -> Rescue:
        """
        Context manager that creates a rescue on the board for use

        automatically assigns

        Args:
            pass through to :class:Rescue 's constructor

            *args (): args to pass to :class:`Rescue` 's constructor
            overwite(bool): overwrite existing rescues
            **kwargs (): keyword arguments to pass to Rescue's constructor

        Yields:
            created rescue object
        """

        rescue = Rescue(*args, board_index=self.free_case_number, **kwargs)
        yield rescue
        # then append it to ourselves
        await self.append(rescue, overwrite=ovewrite)

    async def append(self, rescue: Rescue, overwrite: bool = False) -> None:
        """
        Append a rescue to ourselves



        Args:
            rescue (Rescue): object to append
            overwrite(bool): overwrite existing cases
    """
        if (rescue.api_id in self or rescue.board_index in self) and not overwrite:
            raise ValueError("Attempted to append a rescue that already exists to the board")
        self._storage_by_uuid[rescue.api_id] = rescue
        self._storage_by_index[rescue.board_index] = rescue

        if rescue.client:
            self._storage_by_client[rescue.client] = rescue

    @asynccontextmanager
    async def modify_rescue(self, key: _KEY_TYPE) -> Rescue:
        """
        Context manager to modify a Rescue

        Args:
            key ():

        Returns:

        """

        target = self[key]

        # most tracked attributes may be modified in here, so we pop the rescue
        # from tracking and append it after

        del self[key]

        try:
            yield target
        finally:
            # we need to be sure to re-append the rescue upon completion (so errors don't drop cases)
            await self.append(target)
