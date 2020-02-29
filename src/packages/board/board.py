"""
board.py - rescue board tracking facility


Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from __future__ import annotations

import collections
import itertools
import typing
from asyncio import Lock
from collections import abc
from contextlib import asynccontextmanager
from uuid import UUID

from loguru import logger

from src.config import CONFIG_MARKER
from ..fuelrats_api import FuelratsApiABC
from ..fuelrats_api.v3.mockup import ApiError
from ..rescue import Rescue

cycle_at = 15
"""
Determines at what board index does mecha (attempt) to start over indexing

Notes:
    mecha will still count beyond this value unrestricted, but will attempt
    to keep assigned case numbers below this value whenever possible.
"""

api_url = ""
"""
Fuelrats API location
"""

_KEY_TYPE = typing.Union[str, int, UUID]  # pylint: disable=invalid-name
BoardKey = typing.TypeVar("BoardKey", _KEY_TYPE, Rescue)


@CONFIG_MARKER
def validate_config(data: typing.Dict):  # pylint: disable=unused-argument
    """
    Validate new configuration data.

    Args:
        data (typing.Dict): new configuration data  to validate

    Raises:
        ValueError:  config section failed to validate.
        KeyError:  config section failed to validate.
    """
    if 'board' not in data:
        raise ValueError("board configuration section is missing!")

    if data['board']['cycle_at'] <= 0:
        raise ValueError("constraint cycle_at must be non-zero and positive")

    if data['board']['api_url'] == "":
        raise ValueError("constraint api_url must not be empty.")


# noinspection PyUnusedLocal
@CONFIG_MARKER
def rehash_handler(data: typing.Dict):  # pylint: disable=unused-argument
    """
    Apply new configuration data

    Args:
        data (typing.Dict): new configuration data to apply.

    """
    global cycle_at
    cycle_at = data['board']['cycle_at']


class RatBoard(abc.Mapping):
    """
    The Rat Board
    """
    __slots__ = [
        "_storage_by_uuid",
        "_storage_by_client",
        "_handler",
        "_storage_by_index",
        "_index_counter",
        "_offline",
        "_modification_lock",
        "_recently_closed",
        "_offline_rescue_storage",
        "__weakref__"
    ]

    def __init__(
            self,
            api_handler: typing.Optional[FuelratsApiABC] = None,
            offline: bool = True,
            max_recently_closed=5,
    ):
        self._handler: typing.Optional[FuelratsApiABC] = api_handler
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
        self._offline = offline

        self._modification_lock = Lock()
        """
        Modification lock to prevent concurrent modification of the board.
        """

        self._recently_closed: typing.Deque[Rescue] = collections.deque(maxlen=max_recently_closed)
        """ Recently closed rescue deck """
        self._offline_rescue_storage: typing.Deque[Rescue] = collections.deque()
        """ Holds closed cases that couldn't be pushed to the API (probably due to offline mode) """

        super(RatBoard, self).__init__()

    @property
    def recently_closed(self) -> typing.Deque[Rescue]:
        """ Recently closed rescues """
        return self._recently_closed

    async def on_online(self):
        logger.info("Rescue board online.")
        self._offline = False
        logger.info("emitting {} cached rescues to the API...", len(self._offline_rescue_storage))
        while self._offline_rescue_storage:
            await self._handler.update_rescue(self._offline_rescue_storage.popleft())

    async def on_offline(self):
        logger.warning("Rescue board now offline.")
        self._offline = True

    def __getitem__(self, key: _KEY_TYPE) -> Rescue:
        if isinstance(key, str):
            return self._storage_by_client[key.casefold()]

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
        overflow = next_free >= cycle_at
        if overflow:
            self._index_counter = itertools.count()
            # get the next free index from the underlying magic
            return self._free_case_number

        # return the next index from the magic
        return next_free

    async def append(self, rescue: Rescue, overwrite: bool = False) -> None:
        """
        Append a rescue to ourselves

        Args:
            rescue (Rescue): object to append
            overwrite(bool): overwrite existing cases
    """
        logger.trace("acquiring modification lock...")
        async with self._modification_lock:
            logger.trace("acquired modification lock.")
            if (rescue.api_id in self or rescue.board_index in self) and not overwrite:
                raise ValueError("Attempted to append a rescue that already exists to the board")
            self._storage_by_uuid[rescue.api_id] = rescue
            self._storage_by_index[rescue.board_index] = rescue

            if rescue.client:
                self._storage_by_client[rescue.client.casefold()] = rescue
        logger.trace("released modification lock.")

    @property
    def online(self):
        """ is this module in online mode """
        return not self._offline and self._handler is not None

    def __contains__(self, key: _KEY_TYPE) -> bool:
        if isinstance(key, str):
            return key.casefold() in self._storage_by_client
        if isinstance(key, UUID):
            return key in self._storage_by_uuid
        return key in self._storage_by_index

    def __delitem__(self, key: _KEY_TYPE):
        # Sanity check.
        if not self._modification_lock.locked():
            raise RuntimeError("attempted to delete a rescue without acquiring the lock first!")
        # Get the target.
        target = self[key]

        # Purge it key by key.
        del self._storage_by_uuid[target.api_id]
        del self._storage_by_index[target.board_index]
        if target.client:
            del self._storage_by_client[target.client.casefold()]

    @asynccontextmanager
    async def modify_rescue(self, key: BoardKey) -> Rescue:
        """
        Context manager to modify a Rescue

        Args:
            key ():

        Yields:
            Rescue: rescue to modify based on its `key`
        """
        logger.trace("acquiring modification lock...")
        async with self._modification_lock:
            logger.trace("acquired modification lock.")
            if isinstance(key, Rescue):
                key = key.board_index

            target = self[key]

            # most tracked attributes may be modified in here, so we pop the rescue
            # from tracking and append it after

            del self[key]

            self._modification_lock.release()
            try:
                # Yield so the caller can modify the rescue
                yield target

            finally:
                # we need to be sure to re-append the rescue upon completion
                # (so errors don't drop cases)
                await self.append(target)
                # append will reacquire the lock, so don;t reacquire it ourselves (damn no rlocks),
                # but the context manger is gunna freak out if we don't re-acquire it though.
                await self._modification_lock.acquire()

            # If we are in online mode, emit update event to API.
            if self.online:
                logger.trace("updating API...")
                await self._handler.update_rescue(target)

        logger.trace("released modification lock.")

    async def create_rescue(self, *args, ovewrite=False, **kwargs) -> Rescue:
        """
        Creates a rescue, in online mode this will perform creation actions against the API.
        In the event of API error, the rescue will still be created locally, though an exception
        raised.

        Args:
            pass through to :class:Rescue 's constructor

            *args (): args to pass to :class:`Rescue` 's constructor
            overwite(bool): overwrite existing rescues
            **kwargs (): keyword arguments to pass to Rescue's constructor

        Returns:
            created rescue object

        Raises:
            ApiError: Something went wrong in API creation, rescue has been created locally.
        """
        index = self.free_case_number
        rescue = Rescue(*args, board_index=index, **kwargs)

        try:
            if not self.online:
                logger.warning("creating case in offline mode...")
            else:
                logger.trace("creating rescue on API...")
                rescue = await self._handler.create_rescue(rescue)

        except ApiError:
            logger.exception("unable to create rescue on API!")
            # Emit upstream so the caller knows something went wrong
            raise

        finally:
            rescue.board_index = index
            # Always append it to ourselves, regardless of API errors
            await self.append(rescue, overwrite=ovewrite)

        return rescue

    async def remove_rescue(self, target: BoardKey):
        """ removes a rescue from active tracking """
        if isinstance(target, Rescue):
            target = target.board_index

        case = self[target]
        self._recently_closed.append(case)

        logger.trace("Acquiring modification lock...")
        with self._modification_lock:
            logger.trace("Acquired modification lock.")
            del self[target]
        logger.trace("Released modification lock.")
        # TODO: emit API call
