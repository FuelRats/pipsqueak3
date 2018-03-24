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

    def search(self, index: int = None, client: str = None, api_id: UUID = None) -> Rescue or None:
        """
        Searches for and returns a rescue for a given Index / client name / api id, should it exist
            Will match the first found case matching at least one of the parameters.

        At least one of the parameters must not be None.

        Args:
            index (int): Rescue at given board index, may be None
            client (str): client's commander name / irc nickname, may be None
            api_id (UUID): api id of rescue, may be None

        Returns:
            Rescue: Found rescue on the board, otherwise None

        Raises:
            ValueError: command invoked without params, or all params are None
        """

        # lets check if we have an index, which may be zero
        found: Rescue = None
        if index is not None:
            try:
                found = self._rescues[index]
            except KeyError:
                pass
        if client:
            for key in self._rescues:
                rescue = self._rescues[key]
                if rescue.client == client:
                    found = rescue
        elif api_id:
            for rescue in self._rescues.items():
                LOG.debug(f"comparing rescue={rescue}")
                if rescue[1].case_id == api_id:
                    found = rescue[1]

        return found

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
