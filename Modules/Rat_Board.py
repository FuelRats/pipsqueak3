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

    def __init__(self, handler=None):
        """
        Create a new Rescue Board.

        Args:
            handler (): WS API handler
        """
        self.handler = handler
        self._rescues = {}
        """Rescue objects tracked by this board"""

    def __contains__(self, item: Rescue) -> bool:
        """
        Checks if a rescue exists on this RescueBoard

        Args:
            item (Rescue):

        Returns:
            bool: if item exists
        """
        if not isinstance(item, Rescue):
            raise TypeError
        else:
            for rescue in self._rescues.values():
                if rescue == item:
                    return True
            return False

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
            found = self._rescues[index]
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
        for index, rescue in self._rescues.items():
            if rescue.client == client:
                return rescue

    def find_by_uuid(self, guid: UUID) -> Rescue or None:
        """
        Searches for and returns a rescue by api ID, should it exist.

        Args:
            guid (UUID): uuid to search for

        Returns:
            Rescue: found rescue
            None:   no rescue found

        """
        for index, rescue in self._rescues.items():
            if rescue.case_id == guid:
                return rescue

    def append(self, rescue: Rescue, overwrite: bool = False) -> None:
        """
        Accept a Rescue object and attach it to the board

        Args:
            rescue (Rescue): Rescue object to attach
            overwrite(bool) : **overwrite** existing keys, if necessary

        Returns:
            None

        Raises:
            IndexNotFreeError: Attempt to write a rescue to a key that is already set.
        """
        # if the rescue already has a board index defined
        if rescue.board_index:
            # check if the board index is not in use, or the overwrite flag is set
            if overwrite or rescue.board_index not in self._rescues:
                # TODO: check this logic via unit tests
                # write the key,value
                self._rescues[rescue.board_index] = rescue
            else:
                raise IndexNotFreeError(
                    f"Index {rescue.board_index} is in use. If you want to overwrite this you must"
                    f"set the `overwrite` flag.")

    def modify(self, rescue: Rescue) -> bool:
        """
        Modify an existing Rescue on the board

        Args:
            rescue (Rescue): new Rescue object to replace existing

        Returns:
            True IF rescue exists and was replaced
            False if rescue does not exist or was not modified.
        """
        # TODO: implement modify(), until then its marked nocover.
        return False  # PRAGMA: NOCOVER

    def remove(self, rescue: Rescue) -> None:
        """
        Removes a case from the board

        Args:
            rescue (Rescue): Rescue to remove

        Returns:
            None

        Raises:
            KeyError: rescue was not on the board.
        """
        self._rescues.pop(rescue.board_index)

    def clear_board(self) -> None:
        """
        Clears all tracked cases.
        """
        LOG.warning("Flushing the Dispatch Board, fire in the hole!")
        self._rescues = {}
