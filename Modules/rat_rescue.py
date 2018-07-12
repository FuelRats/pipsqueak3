"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import logging
from contextlib import contextmanager
from datetime import datetime
from functools import reduce
from operator import xor
from typing import Union, Optional, List
from uuid import UUID

from Modules.epic import Epic
from Modules.mark_for_deletion import MarkForDeletion
from Modules.rat_cache import RatCache
from Modules.rat_quotation import Quotation
from Modules.rat import Rat
from utils.ratlib import Platforms, Status

log = logging.getLogger(f"mecha.{__name__}")


class Rescue(object):
    """
    A unique rescue
    """

    def __init__(self, uuid: UUID,
                 client: str,
                 system: str,
                 irc_nickname: str,
                 board: 'RatBoard' = None,
                 created_at: datetime = None,
                 updated_at: datetime = None,
                 unidentified_rats=None,
                 active=True,
                 quotes: list = None,
                 epic: List[Epic] = None,
                 title: Optional[str] = None,
                 first_limpet: Optional[UUID] = None,
                 board_index: Optional[int] = None,
                 mark_for_deletion: MarkForDeletion = MarkForDeletion(),
                 lang_id: str = "EN",
                 rats: List[Rat] = None,
                 status: Status = Status.OPEN,
                 code_red=False):
        """
        creates a unique rescue

        Args:

            code_red (bool): is the client on emergency oxygen
            status (Status): status attribute for the rescue
            board (RatBoard): RatBoard instance this rescue is attached to, if any.
            uuid (str): API id of rescue
            client (str): Commander name of the Commander rescued
            system (str): System name the Commander is stranded in
                (WILL BE CAST TO UPPER CASE)
            created_at (datetime): time the case was first created
                **( READONLY )**
            updated_at (datetime): last tme the case was modified
            unidentified_rats (list): list of unidentified rats responding to
                rescue **(nicknames)**
            active (bool): marks whether the case is active or not
            quotes (list): list of Quotation objects associated with rescue
            epic (bool): is the case marked as an epic
            title (str): name of operation, if applicable
            first_limpet (UUID): Id of the rat that got the first limpet
            board_index (int): index position on the board, if any.
            mark_for_deletion (dict): the markForDeltion object for the API,
                if any.
                - will default to open and not MD'ed
            lang_id (str): language ID of the client, defaults to english.
            irc_nickname (str): clients IRC nickname, may deffer from their
                commander name.
            rats (list): identified (Rat)s assigned to rescue.
        """
        self._platform: Platforms = Platforms.DEFAULT
        self.rat_board: 'RatBoard' = board
        self._rats = rats if rats else []
        self._createdAt: datetime = created_at if created_at else datetime.utcnow()
        self._updatedAt: datetime = updated_at if updated_at else datetime.utcnow()
        self._id: UUID = uuid
        self._client: str = client
        self._irc_nick: str = irc_nickname
        self._unidentified_rats = unidentified_rats if unidentified_rats else []
        self._system: str = system.upper()
        self._active: bool = active
        self._quotes: list = quotes if quotes else []
        self._epic: List[Epic] = epic if epic is not None else []
        self._codeRed: bool = code_red
        self._outcome: None = None
        self._title: Union[str, None] = title
        self._firstLimpet: UUID = first_limpet
        self._board_index = board_index
        self._mark_for_deletion = mark_for_deletion
        self._board_index = board_index
        self._lang_id = lang_id
        self._status = status
        self._hash = None

    def __eq__(self, other) -> bool:
        """
        Verify `other` is equal to the elf.

        Args:
            other (Rescue): Rescue to compare against

        Returns:
            bool: is equivalent
        """
        if not isinstance(other, Rescue):
            # instance type check
            return NotImplemented
        else:
            # check equality

            conditions = [
                self.uuid == other.uuid,
                self.board_index == other.board_index,
                self.client == other.client,
                self.rats == other.rats,
                self.platform == other.platform,
                self.first_limpet == other.first_limpet,
                self.created_at == other.created_at,
                self.updated_at == other.updated_at,
                self.system == other.system,
                self.unidentified_rats == other.unidentified_rats,
                self.active == other.active,
                self.code_red == other.code_red,
                self.outcome == other.outcome,
                self.title == other.title,
                self.first_limpet == other.first_limpet,
                self.marked_for_deletion == other.marked_for_deletion,
                self.lang_id == other.lang_id,
                self.rats == other.rats,
                self.irc_nickname == other.irc_nickname,
            ]

            return all(conditions)

    def __hash__(self):

        if self._hash is None:
            attributes = (
                self.uuid,
                self.board_index,
                self.client,
                self.platform,
                self.first_limpet,
                self.created_at,
                self.updated_at,
                self.system,
                self.active,
                self.code_red,
                self.outcome,
                self.title,
                self.first_limpet,
                self.lang_id,
                self.irc_nickname,
            )

            self._hash = reduce(xor, map(hash, attributes))
        return self._hash

    @property
    def status(self) -> Status:
        """
        Status enum for the rescue

        Returns:
            Status
        """
        return self._status

    @status.setter
    def status(self, value: status):
        """
        Set the value of the status enum

        Args:
            value (Status): new status enum

        Raises:
            TypeError: invalid `value` type
        """
        if isinstance(value, Status):
            self._status = value
        else:
            raise TypeError

    @property
    def irc_nickname(self) -> str:
        """
        The client's irc nickname

        Returns:
            str : nickname
        """
        return self._irc_nick

    @irc_nickname.setter
    def irc_nickname(self, value: str) -> None:
        """
        Sets the client's irc nickname

        Args:
            value (str): new nickname

        Raises:
             TypeError : value was not a string.
        """
        if isinstance(value, str):
            self._irc_nick = value
        else:
            raise TypeError

    @property
    def lang_id(self) -> str:
        """
        The language ID the client reported upon entering
        Returns:
            str: clients language ID
        """
        return self._lang_id

    @lang_id.setter
    def lang_id(self, value) -> None:
        """
        Sets the client's language

        Args:
            value (str): new lagnuage code
        """
        if isinstance(value, str):
            self._lang_id = value
        else:
            raise TypeError

    @property
    def platform(self):
        """The Rescue's platform"""
        return self._platform

    @platform.setter
    def platform(self, value) -> None:
        """
        Set the client's platform

        Args:
            value (Platforms): new platform
        """
        if isinstance(value, Platforms):
            self._platform = value
        else:
            raise TypeError(f"expected a Platforms, got type {type(value)}")

    @property
    def first_limpet(self) -> UUID:
        """
        The ratID of the rat that got the first limpet

        Returns:
            str : ratid
        """
        return self._firstLimpet

    @first_limpet.setter
    def first_limpet(self, value: UUID) -> None:
        """
        Set the value of the first limpet rat

        If the value is not a UUID, this method will attempt to coerce it into one.

        Args:
            value (UUID): rat id of the first-limpet rat.

        Returns:
            None

        Raises:
            ValueError: The value was not a UUID and could not be parsed into a valid one.
        """
        if isinstance(value, UUID):
            self._firstLimpet = value
        else:
            # the value wasn't a uuid, but lets try and coerce it into one.
            try:
                # try parse
                guid = UUID(value)
            except (ValueError, AttributeError):
                # the attempt failed
                raise TypeError(f"expected UUID, got type {type(value)}")
            else:
                # the attempt succeeded, lets assign it.
                self._firstLimpet = guid

    @property
    def board_index(self) -> int or None:
        """
        The position on the rescue board this rescue holds, if any.

        Returns:
            int: if the board is attached to a case, otherwise None
        """
        return self._board_index

    @board_index.setter
    def board_index(self, value: int or None) -> None:
        """
        Sets the Rescue's board index

        Set to None if the rescue is not attached to the board.

        Args:
            value (int or None): index position

        Returns:
            None
        """
        # negative board indexes should not be possible, right?
        if isinstance(value, int) or value is None:
            if value is None or value >= 0:
                self._board_index = value
            else:
                raise ValueError("Value must be greater than or equal to zero,"
                                 " or None.")
        else:
            raise TypeError(f"expected int or None, got {type(value)}")

    @property
    def uuid(self) -> UUID:
        """
        The API Id of the rescue.

        Returns: API id

        """

        return self._id

    @uuid.setter
    def uuid(self, value: UUID) -> None:
        """
        Sets the API uuid associated with the Rescue

        Args:
            value (UUID): The API ID

        Returns:
            None
        """
        if isinstance(value, UUID):
            self._id = value
        else:
            raise ValueError(f"expected UUID, got type {type(value)}")

    @property
    def client(self) -> str:
        """
        The client associated with the rescue

        Returns:
            (str) the client

        """
        return self._client

    @client.setter
    def client(self, value: str) -> None:
        """
        Sets the client's Commander Name associated with the rescue

        Args:
            value (str): Commander name of the client

        Returns:
            None
        """
        self._client = value

    @property
    def created_at(self) -> datetime:
        """
        Case creation time.

        Notes
            this property is **READONLY**.


        It can only be set during Rescue object creation

        Returns:
            datetime: creation date
        """
        return self._createdAt

    @property
    def system(self) -> str:
        """
        The clients system name

        Returns:
            str: the clients system name
        """
        return self._system

    @system.setter
    def system(self, value: str):
        """
        Sets the system property to the upper case of `value`

        Raises:
            AttributeError: if `value` is not a string

        Args:
            value (str): string to set `self.system` to

        Returns:
            None

        Notes:
            this method will cast `value` to upper case, as to comply with
            Fuelrats Api v2.1
        """

        # for API v2.1 compatibility reasons we cast to upper case
        self._system = value.upper()

    @property
    def active(self) -> bool:
        """
        marker indicating whether a case is active or not. this has no direct
         effect on bot functionality,rather its primary function is case
         management.

        Returns:
            bool: Active state
        """
        return False if self.status == Status.INACTIVE else True

    @active.setter
    def active(self, value: bool) -> None:
        """
        setter for `Rescue.active`

        Args:
            value (bool): state to set `active` to.

        Returns:
            None
        """
        if isinstance(value, bool):
            if value:
                self.status = Status.OPEN
            else:
                self.status = Status.INACTIVE
        else:
            raise ValueError(f"expected bool, got type {type(value)}")

    @property
    def quotes(self) -> list:
        """
        Contains all the quotes associated with this Rescue object.

        Elements of the list are Quotation objects

        Returns:
            list: list of Quotation objects
        """
        return self._quotes

    @quotes.setter
    def quotes(self, value) -> None:
        """
        Sets the value of the quotes property to whatever `value` is.

        This should not be set directly outside of case init, rather via
        `add_quote`

        Args:
            value (list): list of Quotation objects

        Returns:
            None
        """
        if isinstance(value, list):
            self._quotes = value
        else:
            raise ValueError(f"expected type list, got {type(value)}")

    def add_quote(self, message: str, author: str or None = None) -> None:
        """
        Helper method, adds a `Quotation` object to the list.

        Use this method to add a Quotation to the Rescue

        Args:
            message (str): Message to quote
            author (str): IRC nickname of who is being quoted, if any.
            Otherwise Defaults to Mecha.

        Returns:
            None
        """
        if author:
            # set the author of the quote
            self.quotes.append(Quotation(author=author, message=message))
        else:
            # otherwise use default
            self.quotes.append(Quotation(message=message))

    @property
    def updated_at(self):
        """
        Last time the rescue object was changed

        Returns:
            datetime
        """

        return self._updatedAt

    @updated_at.setter
    def updated_at(self, value):
        """
        Updates `Rescue.updated_at` property

        Args:
            value (datetime): new last modified datetime

        Raises:
            TypeError: invalid `value` type.
            ValueError: `value` is earlier than creation date.

        Returns:

        """
        if not isinstance(value, datetime):
            raise TypeError(f"Expected datetime, got {type(value)}")
        elif value < self.created_at:
            raise ValueError(f"{value} is older than the cases creation date!")
        else:
            self._updatedAt = value

    @property
    def unidentified_rats(self) -> list:
        """
        List of unidentified rats by their IRC nicknames

        Returns:
            list: unidentified rats by IRC nickname
        """
        return self._unidentified_rats

    @unidentified_rats.setter
    def unidentified_rats(self, value) -> None:
        """
        Sets the value of unidentified_rats

        Args:
            value (list): list of strings

        Raises:
            ValueError: value contained illegal types
            TypeError: value was of an illegal type

        """
        if isinstance(value, list):
            for name in value:
                if isinstance(name, str):
                    self._unidentified_rats.append(name)
                else:
                    raise ValueError(f"Element '{name}' expected to be of type str"
                                     f"str, got {type(name)}")
        else:
            raise TypeError(f"expected type str, got {type(value)}")

    @property
    def open(self) -> bool:
        """
        Helper method for determining if a case is considered open or not

        Returns:
            bool: is case open?

        """
        return self.status is not Status.CLOSED

    @open.setter
    def open(self, value: bool) -> None:
        """
        helper method for setting the Rescue's open status

        Args:
            value (bool): value to set

        Returns:
            None

        Raises:
            TypeError: value was not a boolean
        """
        if isinstance(value, bool):
            if value:
                self.status = Status.OPEN
            else:
                self.status = Status.CLOSED
        else:
            raise TypeError(f"expected type bool, got {type(value)}")

    @property
    def epic(self) -> List[Epic]:
        """
        Epic status of the rescue.

        Returns:
            Epic

        Notes:
            This property is **READ ONLY** (for now)
        """
        return self._epic

    @property
    def code_red(self) -> bool:
        """
        Code Red status for the Rescue

        Returns:
            bool
        """
        return self._codeRed

    @code_red.setter
    def code_red(self, value: bool):
        if isinstance(value, bool):
            self._codeRed = value
        else:
            raise TypeError(f"expected type bool, got {type(value)}")

    @property
    def outcome(self) -> None:
        """
        Success status for Rescue.

        Returns:
            bool
        """
        return self._outcome

    @property
    def title(self) -> str or None:
        """
        The rescues operation title, if any

        Returns:
            str: operation name if set

            None: no name set.
        """
        return self._title

    @title.setter
    def title(self, value: str or None) -> None:
        """
        Set the operations title.

        Args:
            value (str or None): Operation name.

        Returns:
            None

        Raises:
            TypeError: bad value type
        """
        if value is None or isinstance(value, str):
            self._title = value
        else:
            raise TypeError(f"expected type None or str, got {type(value)}")

    @property
    def marked_for_deletion(self) -> MarkForDeletion:
        """
        Mark for deletion object as used by the API

        Returns:
            dict
        """
        return self._mark_for_deletion

    @marked_for_deletion.setter
    def marked_for_deletion(self, value) -> None:
        """
        Sets the Md object

        Args:
            value (MarkForDeletion): value to set the MD object to.

        Returns:
            None

        Raises:
            TypeError: bad value type
        """
        if isinstance(value, MarkForDeletion):
            self._mark_for_deletion = value
        else:
            raise TypeError(f"got {type(value)} expected MarkForDeletion object")

    @property
    def rats(self) -> List[Rat]:
        """
        Identified rats assigned to rescue

        Returns:
            list: identified rats by UUID
        """
        return self._rats

    @rats.setter
    def rats(self, value):
        """
        Sets the rats property directly, it is recommended to use the helper
        methods to add/remove rats.

        Args:
            value (list): new value for `rats`

        Returns:

        """
        if isinstance(value, list):
            self._rats = value

        else:
            raise TypeError(f"expected type list got {type(value)}")

    async def add_rat(self,
                      name: str = None,
                      guid: UUID or str = None,
                      rat: Rat = None) -> Optional[Rat]:
        """
        Adds a rat to the rescue. This method should be run inside a `try` block, as failures will
        be raised as exceptions.

        this method will attempt to coerce `guid:str` into a UUID and may fail in
            spectacular fashion

        Args:
            rat (Rat): Existing Rat object to assign.
            name (str): name of a rat to add
            guid (UUID or str): api uuid of the rat, used if the rat is not found in the cache
                - if this is a string it will be type coerced into a UUID
        Returns:
            Rat: the added rat object

        Raises:
            ValueError: guid was of type `str` and could not be coerced.
            ValueError: Attempted to assign a Rat that does not have a UUID.

        Examples:
            ```python

            ```
        """
        assigned_rat: Optional[Rat] = None

        if isinstance(rat, Rat):
            # we already have a rat object, lets verify it has an ID and assign it.
            if rat.uuid is not None:
                self.rats.append(rat)
                assigned_rat = rat
            else:
                raise ValueError("Assigned rat does not have a known API ID")

        if isinstance(name, str):
            # lets check if we already have this rat in the cache (platform, any)
            found = (await RatCache().get_rat_by_name(name, self.platform),
                     await RatCache().get_rat_by_name(name))
            if found[0]:
                self.rats.append(found[0])
                assigned_rat = found[0]
            elif found[1]:
                # a generic match (not platform specific) was found
                # TODO throw a warning so the invoking method can handle this condition
                log.warning("A match was found, but it was not the right platform!")
                self.rats.append(found[1])
                assigned_rat = found[1]

            else:
                # lets make a new Rat!
                # if self.rat_board:  # PRAGMA: NOCOVER
                #    pass  # TODO fetch rat from API
                # TODO: fetch rats from API handler, use that data to make a new Rat instance

                rat = Rat(name=name, uuid=guid)
                self.rats.append(rat)
                assigned_rat = rat

        elif guid is not None:
            if isinstance(guid, str):
                # attempt to coerce into a UUID
                parsed_guid = UUID(guid)
            elif isinstance(guid, UUID):
                parsed_guid = guid
            else:
                raise ValueError(f"Expected str/UUID, got {type(guid)}")

            # lets check if we already have this rat in the cache
            found = await RatCache().get_rat_by_uuid(parsed_guid)
            if found:
                self.rats.append(found)
                assigned_rat = found
            else:
                pass  # TODO: placeholder for fetching rats from the API handler

        return assigned_rat

    def mark_delete(self, reporter: str, reason: str) -> None:
        """
        Marks a rescue for deletion

        Args:
            reporter (str): person marking rescue as deleted
            reason (str): reason for the rescue being marked as deleted.

        Raises:
            TypeError: invalid params
        """
        # type enforcement
        if not isinstance(reporter, str) or not isinstance(reason, str):
            raise TypeError(f"reporter and/or reason of invalid type. got {type(reporter)},"
                            f"{type(reason)}")

        log.debug(f"marking rescue @{self.uuid} for deletion. reporter is {reporter} and "
                  f"their reason is '{reason}'.")
        if reason == "":
            raise ValueError("Reason required.")
        self.marked_for_deletion.reporter = reporter
        self.marked_for_deletion.reason = reason
        self.marked_for_deletion.marked = True

    def unmark_delete(self) -> None:
        """
        helper method for unmarking a rescue for deletion. resets the Md object
        """

        self.marked_for_deletion.marked = False
        self.marked_for_deletion.reason = None
        self.marked_for_deletion.reporter = None

    @contextmanager
    def change(self):
        """
        Convenience method for making safe attribute changes.

        FIXME: currently just ensures rescue.updated_at is updated.

        TODO: replace with Board context manager once its implemented

        TODO: replace current context manager with a dummy once the Board
            context manager is a thing.

        TODO: implement API integration (probably in the board Contextmanager

        Returns:
            contextManager


        Examples:
            ```

            with rescue.change():
                rescue.client = foo

            ```
        """
        yield
        self.updated_at = datetime.utcnow()

    # TODO: to/from json
    # TODO: track changes
    # TODO: helper method for adding / editing quotes
