"""
rat_board.py - Rescue board

Handles Tracking individual Rescues from creation to completion

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import logging
from typing import Union, Optional
from uuid import UUID

import config
from Modules.rat_rescue import Rescue
from config import config

log = logging.getLogger(f"mecha.{__name__}")


class RescueBoardException(BaseException):
    """
    Generic Rescue Board Exception
    """

    def __init__(self, *args: object) -> None:
        log.error(f"Rescueboard Exception raised!\nargs = {args}")
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
                log.debug(f"Checking rescue {rescue} against {other}...\n"
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

        index = 0
        free = False

        while not free:
            free = index not in self.rescues
            index += 1 if not free else 0

        return index

    def find_by_index(self, index: int) -> Optional[Rescue]:
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
            return None
        else:
            # we found something
            return found

    def find_by_name(self, client: str) -> Optional[Rescue]:
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

    def find_by_uuid(self, guid: UUID) -> Optional[Rescue]:
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

    def search(self, case: Union[str, int, UUID]) -> Optional[Rescue]:
        """
        Helper for searching for a case using implemented search functions.

        Args:
            case (Union[str, int, UUID]): the client's name, a case ID, or a rescue UUID

        Returns:
            Rescue: found rescue
            None:   No rescue found

        Raises:
            ValueError: argument was not an expected type
        """
        # ensure a proper type was passed
        if not isinstance(case, str) and not isinstance(case, int) and not isinstance(case, UUID):
            raise ValueError

        if isinstance(case, str):
            # strings could be any of the valid types (such as using commands), check for the best one.
            if case.isdigit():
                    return self.find_by_index(int(case))
            else:
                # UUIDs always start with @ and are 37 characters, so try to parse it
                if case[0] == "@" and len(case) == 37:
                    try:
                        guid = UUID(case[1:])
                    except (AttributeError, ValueError):
                        # not a valid UUID
                        return None
                    else:
                        return self.find_by_uuid(guid)
                else:
                    return self.find_by_name(case)
        elif isinstance(case, int) and not isinstance(case, bool):
            return self.find_by_index(case)
        else:
            return self.find_by_uuid(case)

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
            rescue.board_index = self.next_free_index()
            self.rescues[rescue.board_index] = rescue

    async def modify(self, rescue: Rescue) -> bool:
        """
        Modify an existing Rescue on the board

        Args:
            rescue (Rescue): new Rescue object to replace existing

        Returns:
            True IF rescue exists and was replaced
            False if rescue does not exist.

        Raises:
            RescueNotChangedException: rescue was not actually changed
        """

        # find the case in question
        found = self.find_by_index(rescue.board_index)

        if found is None:
            # we did not find a rescue to modify
            result = False
        # check if its equal to what we already have
        elif found == rescue:
            log.debug("A call was made to modify, yet the rescue was not changed!")
            raise RescueNotChangedException
        else:
            # its not what we already have

            # lets check if we have a API handler
            if self.handler is not None:
                log.debug("Rescue has been modified, making a call to the API")
                # if so, let it know we changed the rescue
                # FIXME: change to match API Handler interface, once it exists
                await self.handler.update_rescue(rescue)

            log.debug(f"Updating local rescue #{rescue.board_index} (@{rescue.case_id}...")
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
        if self.handler is not None:
            log.debug(f"Calling API to remove case by id {rescue.case_id}")
            #  PRAGMA: NOCOVER
            # FIXME: Do stuff with the API handler, once we know what the interface looks like.
            await self.handler.update_rescue(rescue)
        log.debug(f"Removing case #{rescue.board_index} "
                  f"(@{rescue.case_id})from the board.")
        self.rescues.pop(rescue.board_index)

    def clear_board(self) -> None:
        """
        Clears all tracked cases.

        This method causes Mecha to forget any and all open cases it was tracking, but **does not
            clear them on the API.**

        useful for flushing the board prior to re-retrieving cases from the API
        """
        log.warning("Flushing the Dispatch Board, fire in the hole!")
        self.rescues = {}

    async def retrieve_open_cases_from_api(self) -> None:
        """
        Async method for fetching all **open** cases from the API and appending them to
            the boards `rescue` property for tracking.

        Returns:
            None

        Raises:
            RescueBoardException: no API handler registered for this case.
        """
        # verify we have an API handler registered
        if self.handler is not None:
            log.debug("API handler is registered, attempting to fetch open cases")
            # FIXME:  modify call to match API handler interface once it is implemented
            self.rescues = await self.handler.get_rescues("open")

        else:
            # we don't have a registered API handler, this call cannot succeed,
            log.exception("No API handler is registered, this call will fail!")

            # TODO: replace this exception with something more specific?
            raise RescueBoardException("no API handler registered!")
