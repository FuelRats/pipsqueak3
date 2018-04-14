"""
Rat_Board.py - Rescue board

Handles Tracking individual Rescues from creation to completion

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import logging
from uuid import UUID

from Modules.rat_rescue import Rescue
from config import Logging

LOG = logging.getLogger(f"{Logging.base_logger}.{__name__}")


class RescueBoardException(BaseException):
    """
    Generic Rescue Board Exception
    """

    def __init__(self, *args: object) -> None:
        LOG.error(f"Rescueboard Exception raised!\nargs = {args}")
        super().__init__(*args)


class RescueNotFoundException(RescueBoardException):
    """
    Exception raised when a Rescue was not found
    """
    pass


class RescueNotChangedException(RescueBoardException):
    """
    Exception raised when there was no net change to a Rescue.
    """
    pass


class IndexNotFreeError(RescueBoardException):
    """ Exception raised when someone attempts to attach a Rescue to a board index in-use"""
    pass


class RatBoard(object):
    """
    A rescue board
    """
    # i dread the day where we need to upp this limit.

    indexies = set(range(30))

    """set of indexies that can be used"""
    def __init__(self, handler=None):
        """
        Create a new Rescue Board.

        Args:
            handler (): WS API handler
        """
        self.handler = handler
        """API handler used by the board"""
        self._rescues = {}
        """Rescue objects tracked by this board"""
        self._last_index: int = None
        """Last index used by the board during case creation"""

    def __contains__(self, other: Rescue) -> bool:
        """
        Checks if a rescue exists on this

        First, this method will check if the `other` object has a uuid that matches an existing
            rescue on the board. If

        If the uuid is not known, it will check the `other` objects key attributes against all
            tracked rescues to try and find a match

            Key attributes are:
                - client
                - created_at

        Args:
            other (Rescue):

        Returns:
            bool: if item exists
        """
        if not isinstance(other, Rescue):
            raise TypeError
        else:
            for rescue in self.rescues.values():
                LOG.debug(f"checking rescue {rescue} against {other}...\n"
                          f"client {rescue.client} == {other.client} &&  "
                          f"createdAt {rescue.created_at} == {other.created_at}")

                # if the IDs match then we know they are the same case.
                if other.case_id is not None and rescue.case_id == other.case_id:
                    return True

                # check if the key attributes are equal
                elif rescue.client == other.client and rescue.created_at == other.created_at:
                    return True
            # no matches
            return False

    @property
    def rescues(self) -> dict:
        """
        Rescues tracked by the board

        Returns:
            dict: rescues by board index
        """
        return self._rescues

    @rescues.setter
    def rescues(self, value) -> None:
        """
        Set the tracked rescues
        Args:
            value (dict):

        Returns:
            None
        """
        if isinstance(value, dict):
            self._rescues = value
        else:
            raise TypeError

    def next_free_index(self) -> int:
        """
        Helper method that returns the next free case index

        Returns:
            int: next free board index
        """
        consumed = set(self.rescues.keys())

        # subtract the used keys from the list of possible keys
        free = RatBoard.indexies - consumed
        # convert it to a list to access the first element, because sets can't be indexed >.>
        # this might not be the best approach, but it should work.
        return list(free)[0]

    def find_by_index(self, index: int) -> Rescue or None:
        """
        Searches for and returns a Rescue at a given `index` position, should it exist

        Args:
            index (int): case number to return

        Returns:
            Rescue: rescue found
            None: no rescue found

        """
        try:
            found = self.rescues[index]
        except KeyError:
            # the key doesn't exist, therefore no rescue at that index.
            pass
        else:
            # we found something
            return found

    def find_by_name(self, client: str) -> Rescue or None:
        """
        Searches for and returns a Rescue for a given client, should it exist.

        Returns:
            Rescue: found rescue
            None:   no such rescue
        """
        for rescue in self.rescues.values():
            if rescue.client == client:
                return rescue
        return None

    def find_by_uuid(self, guid: UUID) -> Rescue or None:
        """
        Searches for and returns a rescue by api ID, should it exist.

        Args:
            guid (UUID): uuid to search for

        Returns:
            Rescue: found rescue
            None:   no rescue found

        """
        for rescue in self.rescues.values():
            if rescue.case_id == guid:
                return rescue
        return None

    def append(self, rescue: Rescue, overwrite: bool = False) -> None:
        """
        Accept a Rescue object and attach it to the board

        Args:
            rescue (Rescue): Rescue object to attach
            overwrite(bool) : **overwrite** existing keys, if necessary.
                requires `rescue` to have a `board_index` set, otherwise it does nothing.

        Returns:
            None

        Raises:
            IndexNotFreeError: Attempt to write a rescue to a key that is already set.
        """
        # if the rescue already has a board index defined
        if rescue.board_index is not None:
            # check if the board index is not in use, or the overwrite flag is set
            if overwrite or rescue.board_index not in self.rescues:
                # write the key,value
                self.rescues[rescue.board_index] = rescue
            else:
                raise IndexNotFreeError(
                    f"Index {rescue.board_index} is in use. If you want to overwrite this you must"
                    f"set the `overwrite` flag.")

        # we need to give it one
        else:
            #  iterate _last_index until we get a unused value.
            while self._last_index in self.rescues:
                self._last_index += 1

            rescue.board_index = self._last_index
            self.rescues[rescue.board_index] = rescue

    async def modify(self, rescue: Rescue) -> bool:
        """
        Modify an existing Rescue on the board

        Args:
            rescue (Rescue): new Rescue object to replace existing

        Returns:
            True IF rescue exists and was replaced
            False if rescue does not exist or was not modified.
        """

        result = False

        # find the case in question
        found = self.find_by_index(rescue.board_index)
        # check if its equal to what we already have
        if found == rescue:
            result = False
        else:
            # its not what we already have

            # lets check if we have a API handler
            if self.handler is not None:
                # if so, let it know we changed the rescue
                # PRAGMA : NOCOVER
                # FIXME: change to match API Handler interface, once it exists
                await self.handler.update_rescue(rescue)

            self.append(rescue=rescue, overwrite=True)
            result = True

        return result

    async def remove(self, rescue: Rescue) -> None:
        """
        Removes a case from the board

        Args:
            rescue (Rescue): Rescue to remove

        Returns:
            None

        Raises:
            KeyError: rescue was not on the board.
        """
        if self.handler is not None:  # PRAGMA : NOCOVER
            # FIXME: Do stuff with the API handler, once we know what the interface looks like.
            await self.handler.update_rescue(rescue)

        self.rescues.pop(rescue.board_index)

    def clear_board(self) -> None:
        """
        Clears all tracked cases.
        """
        LOG.warning("Flushing the Dispatch Board, fire in the hole!")
        self.rescues = {}
