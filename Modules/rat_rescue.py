"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import logging
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

import config
from Modules.rat_quotation import Quotation
from Modules.rats import Rats
from ratlib.names import Platforms

LOG = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


class Rescue(object):
    """
    A unique rescue
    """

    def __init__(self, case_id: UUID, client: str, system: str, irc_nickname: str,
                 board: 'RatBoard' = None, created_at: datetime = None, updated_at: datetime = None,
                 unidentified_rats=None, active=True, quotes: list = None, is_open=True, epic=False,
                 code_red=False, successful=False, title: str = '',
                 first_limpet: UUID or None = None, board_index: int = None,
                 mark_for_deletion: list or None = None, lang_id: str = "EN", rats: list = None):
        """
        creates a unique rescue

        Args:

            board (RatBoard): RatBoard instance this rescue is attached to, if any.
            case_id (str): API id of rescue
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
            is_open (bool): is the case marked as open
            epic (bool): is the case marked as an epic
            code_red (bool): is the case marked as a Code Red
            successful (bool): is the case marked as a success
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
        self._id: UUID = case_id
        self._client: str = client
        self._irc_nick: str = irc_nickname
        self._unidentified_rats = unidentified_rats if unidentified_rats else []
        self._system: str = system.upper()
        self._active: bool = active
        self._quotes: list = quotes if quotes else []
        self._open: bool = is_open
        self._epic: bool = epic
        self._codeRed: bool = code_red
        self._successful: bool = successful
        self._title: str = title
        self._firstLimpet: UUID = first_limpet
        self._board_index = board_index
        self._mark_for_deletion = mark_for_deletion if mark_for_deletion else {
            "marked": False,
            "reason": None,
            "reporter": "Noone."
        }
        self._board_index = board_index
        self._lang_id = lang_id

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
            raise TypeError(f"other was of type {type(other)} expected instance of Rescue")
        else:
            # check equality
            try:
                assert self.case_id == other.case_id
                assert self.board_index == other.board_index
                assert self.client == other.client
                assert self.rats == other.rats
                assert self.platform == other.platform
                assert self.first_limpet == other.first_limpet
                assert self.created_at == other.created_at
                assert self.updated_at == other.updated_at
                assert self.system == other.system
                assert self.unidentified_rats == other.unidentified_rats
                assert self.active == other.active
                assert self.code_red == other.code_red
                assert self.successful == other.successful
                assert self.title == other.title
                assert self.first_limpet == other.first_limpet
                assert self.mark_for_deletion == other.mark_for_deletion
                assert self._lang_id == other._lang_id  # TODO: implement property
                assert self.rats == other.rats
                assert self._irc_nick == other._irc_nick  # TODO: implement property
            except AssertionError as ex:
                raise ex
                # if at least one of the above statements is false.
                return False
            else:
                # no error, the two instances are equal.
                return True

    @property
    def platform(self):
        """The Rescue's platform"""
        return self._platform

    @platform.setter
    def platform(self, value):
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
    def case_id(self) -> UUID:
        """
        The API Id of the rescue.

        Returns: API id

        Notes:
            This field is **READ ONLY**
        """

        return self._id

    @property
    def client(self) -> str:
        """
        The client associated with the rescue\n
        Returns:
            (str) the client

        """
        return self._client

    @client.setter
    def client(self, name) -> None:
        """
        Sets the client's Commander Name associated with the rescue
        Args:
            name (str): Commander name of the client

        Returns:
            None
        """
        self._client = name

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
        return self._active

    @active.setter
    def active(self, value) -> None:
        """
        setter for `Rescue.active`

        Args:
            value (bool): state to set `active` to.

        Returns:
            None
        """
        if isinstance(value, bool):
            self._active = value
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
    def unidentified_rats(self, value):
        if isinstance(value, list):
            for name in value:
                if isinstance(name, str):
                    self._unidentified_rats.append(name)
                else:
                    raise TypeError(f"Element '{name}' expected to be of type str"
                                    f"str, got {type(name)}")
        else:
            raise TypeError(f"expected type str, got {type(value)}")

    @property
    def is_open(self) -> bool:
        """
        Bool storing the Rescue's open status.

        - this cannot be named `Rescue.open` as it would shadow the name from
        the outer scope (bad)

        Returns:
            bool: is case open?

        """
        return self._open

    @is_open.setter
    def is_open(self, value: bool) -> None:
        """
        Set the Rescue's open status

        Args:
            value (bool): value to set

        Returns:
            None

        Raises:
            TypeError: value was not a boolean
        """
        if isinstance(value, bool):
            self._open = value
        else:
            raise TypeError(f"expected type bool, got {type(value)}")

    @property
    def epic(self) -> bool:
        """
        Epic status of the rescue.

        Returns:
            bool

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
    def successful(self) -> bool:
        """
        Success status for Rescue.

        Returns:
            bool
        """
        return self._successful

    @successful.setter
    def successful(self, value: bool) -> None:
        """
        sets the success state for the rescue

        Args:
            value (bool): success status

        Returns:
            None

        Raises:
            TypeError: bad `value` type
        """
        if isinstance(value, bool):
            self._successful = value
        else:
            raise TypeError(f"expected type bool, got {type(value)}")

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
    def mark_for_deletion(self) -> dict:
        """
        Mark for deletion object as used by the API

        Returns:
            dict
        """
        return self._mark_for_deletion

    @mark_for_deletion.setter
    def mark_for_deletion(self, value) -> None:
        """
        Sets the Md object

        Args:
            value (dict): value to set the MD object to.

        Returns:
            None

        Raises:
            TypeError: bad value type
            ValueError: value failed validation
        """
        if isinstance(value, dict):
            # checks to ensure only the required fields are present
            if "marked" in value and "reason" in value and "reporter" in value\
                    and len(value) == 3:
                self._mark_for_deletion = value
            else:
                LOG.debug(f"data of value is: {value}")
                raise ValueError("required fields missing and/or garbage "
                                 "data present!")
        else:
            raise TypeError(f"expected type dict, got type {type(value)}")

    @property
    def rats(self) -> list:
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

    def add_rat(self, name: str = None, guid: UUID or str = None, rat: Rats = None) -> None:
        """
        Adds a rat to the rescue. This method should be run inside a `try` block, as failures will
        be raised as exceptions.

        this method will attempt to coerce `guid:str` into a UUID and may fail in
            spectacular fashion

        Args:
            rat (Rats): Existing Rat object to assign.
            name (str): name of a rat to add
            guid (UUID or str): api uuid of the rat, used if the rat is not found in the cache
                - if this is a string it will be type coerced into a UUID
        Returns:
            None:

        Raises:
            ValueError: guid was of type `str` and could not be coerced.
            ValueError: Attempted to assign a Rat that does not have a UUID.

        Examples:
            ```python

            ```
        """
        if isinstance(rat, Rats):
            # we already have a rat object, lets verify it has an ID and assign it.
            if rat.uuid is not None:
                self.rats.append(rat)
                return
            else:
                raise ValueError("Assigned rat does not have a known API ID")

        if isinstance(name, str):
            # lets check if we already have this rat in the cache
            found = Rats.get_rat(name, self.platform)
            if found:
                self.rats.append(found)
                return


        else:
            # lets make a new Rat!
            if self.rat_board:  # PRAGMA: NOCOVER
                raise NotImplementedError  # TODO fetch rat from API
            # TODO: fetch rats from API handler, use that data to make a new Rats instance

            rat = Rats(name=name, uuid=guid)
            self.rats.append(rat)


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
