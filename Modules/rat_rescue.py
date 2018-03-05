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
from Modules.trigger import Trigger

log = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


class Rats(object):
    """
    This class keeps track of known rats as they are used and stores them in a class cache.

    Instances of this class are used to represent a unique, individual rat.

    Creation of a `Rats` object will automatically add the created rat to the cache,
    allowing convenience method `Rats.get_rat` to return the instance when called.
    """

    cache_by_id = {}
    """Cache of rat objects by their UUID"""
    cache_by_name = {}
    """Cache of rat objects by rat name (str)"""

    def __init__(self, uuid: UUID, name: str=None):
        """
        Creates a new rat

        Args:
            uuid (UUID):
            name (str): rat's name


        """
        # set our properties
        self._uuid = uuid
        self._name = name
        # and update the cache
        if name:
            Rats.cache_by_name[name] = self
        Rats.cache_by_id[uuid] = self

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
        Set the UUID of the rat. accepts a uuid encoded string, or a uuid object.

        Args:
            value (UUID): new uuid for rat

        Returns:
            None
        """
        if isinstance(value, str):
            log.debug(f"value was a string with data '{value}'")
            uuid = UUID(value)
            log.debug("parsed value into a valid UUID.")
            self._uuid = uuid
        elif isinstance(value, UUID):
            self._uuid = value

        else:
            raise TypeError(f"expected type None or type str, got {type(value)}")

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

    @classmethod
    def get_rat(cls, name: str = None, uuid: UUID = None) -> 'Rats' or None:
        """
        Finds a rat either by name or by uuid.

        Will also accept both, and only return if the rat name matches its uuid entry.

        Args:
            name (str): name to search for
            uuid (UUID): uuid to search for

        Returns:
            Rats
        """
        if not name and not uuid:
            raise ValueError("expected either a name or a uuid to search for. got neither.")
        else:
            try:
                if name and not uuid:
                    # we are just looking by a name
                    log.debug(f"searching for name '{name}'...")
                    return cls.cache_by_name[name]
                elif uuid and not name:
                    # just looking by a ID
                    log.debug(f"looking for uuid {uuid}")
                    return cls.cache_by_id[uuid]
                elif uuid and name:
                    # we want an exact match.
                    by_name = cls.cache_by_name[name]
                    by_id = cls.cache_by_id[uuid]
                    if by_id == by_name:
                        return by_id
                    else:
                        # its not a match.
                        log.debug(f"{by_id} does not match {by_name}!")
                        return None
            except IndexError:
                # no such rat in cache
                return None

    @classmethod
    def flush(cls) -> None:
        """
        Flushes the caches.

        Returns:
            None
        """
        cls.cache_by_id = {}
        cls.cache_by_name = {}


class Quotation(object):
    """
    A quotes object, element of Rescue
    """

    def __init__(self, message: str, author="Mecha", created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                 last_author="Mecha"):
        """
        Creates a new Quotation object\n
        :param message: recorded message
        :type message: str
        :param author: who wrote the message
        :type author: str
        :param created_at: time the quote was created
        :type created_at: datetime
        :param updated_at: last time the quote was touched
        :type updated_at: datetime
        :param last_author: Last person to touch the quote
        :type last_author: str
        """
        self._message = message
        self._author = author
        self._created_at = created_at
        self._updated_at = updated_at
        self._last_author = last_author

    @property
    def message(self) -> str:
        """
        Recorded message\n
        :return: message
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, value) -> None:
        """
        Sets the message property\n
        :param value: value to set
        :type value: str
        :return: None
        :rtype: None
        """
        self._message = value

    @property
    def author(self) -> str:
        """
        Original author of message ( READ ONLY )\n
        :return: author
        :rtype: str
        """
        return self._author

    @property
    def created_at(self) -> datetime:
        """
        When the case was created\n
        :return: time of creation
        :rtype: datetime
        """
        return self._created_at

    @property
    def updated_at(self):
        """
        When the quote was last modified\n
        :return: modify time
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        if isinstance(value, datetime):
            self._updated_at = value
        else:
            raise ValueError(f"Expected string got {type(value)}")

    @property
    def last_author(self):
        """
        IRC nickname of the last person to modify this quote
        :return:
        :rtype:
        """
        return self._last_author

    @last_author.setter
    def last_author(self, value):
        if isinstance(value, str):
            self._last_author = value
        else:
            raise ValueError(f"Expected string got {type(value)}")

    def modify(self, event_trigger: Trigger, message: str) -> None:
        """
        Helper method for modifying a quote\n
        Args:
            event_trigger (Trigger): Trigger object of invoking user
            message (str): message to set as quoted text

        Returns: None

        """
        self._message = message
        self._updated_at = datetime.utcnow()
        self._last_author = event_trigger.nickname


class Rescue(object):
    """
    A unique rescue
    """

    def __init__(self, case_id: UUID, client: str, system: str, irc_nickname: str, created_at: datetime = None,
                 updated_at: datetime = None, unidentified_rats=None, active=True, quotes: list = None, is_open=True,
                 epic=False, code_red=False, successful=False, title: str = '', first_limpet: UUID or None = None,
                 board_index: int = None, mark_for_deletion: list or None = None, lang_id: str = "EN",
                 rats: list = None):
        """
        creates a unique rescue

        Args:

            case_id (str): API id of rescue
            client (str): Commander name of the Commander rescued
            system (str): System name the Commander is stranded in (WILL BE CAST TO UPPER CASE)
            created_at (datetime): time the case was first created **( READONLY )**
            updated_at (datetime): last tme the case was modified
            unidentified_rats (list): list of unidentified rats responding to rescue **(nicknames)**
            active (bool): marks whether the case is active or not
            quotes (list): list of Quotation objects associated with rescue
            is_open (bool): is the case marked as open
            epic (bool): is the case marked as an epic
            code_red (bool): is the case marked as a Code Red
            successful (bool): is the case marked as a success
            title (str): name of operation, if applicable
            first_limpet (UUID): Id of the rat that got the first limpet
            board_index (int): index position on the board, if any.
            mark_for_deletion (dict): the markForDeltion object for the API, if any.
             - will default to open and not MD'ed
            lang_id (str): language ID of the client, defaults to english.
            irc_nickname (str): clients IRC nickname, may deffer from their commander name.
            rats (list): identified (Rat)s assigned to rescue.
        """
        self._rats = rats if rats else []
        self._createdAt: datetime = created_at if created_at else datetime.utcnow()
        self._updatedAt: datetime = updated_at if updated_at else datetime.utcnow()
        self._id: UUID = case_id
        self._client: str = client
        self._irc_nick: str = irc_nickname
        self._unidentifiedRats = unidentified_rats if unidentified_rats else []
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

    @property
    def first_limpet(self) -> UUID:
        """
        The ratID of the rat that got the first limpet

        Returns:
            str : ratid
        """
        return self._firstLimpet

    @first_limpet.setter
    def first_limpet(self, value) -> None:
        """
        Set the value of the first limpet rat
        Args:
            value (str): rat id of the first-limpet rat.

        Returns:
            None
        """
        if isinstance(value, UUID):
            self._firstLimpet = value
        else:
            raise TypeError(f"expected UUID, got type {type(value)}")

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
                raise ValueError("Value must be greater than or equal to zero, or None.")
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
            this method will cast `value` to upper case, as to comply with Fuelrats Api v2.1
        """

        # for API v2.1 compatibility reasons we cast to upper case
        self._system = value.upper()

    @property
    def active(self) -> bool:
        """
        marker indicating whether a case is active or not. this has no direct effect on bot functionality,
        rather its primary function is case management.

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

        This should not be set directly outside of case init, rather via `add_quote`

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
            author (str): IRC nickname of who is being quoted, if any. Otherwise Defaults to Mecha.

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
        return self._unidentifiedRats

    @unidentified_rats.setter
    def unidentified_rats(self, value):
        if isinstance(value, list):
            for name in value:
                if isinstance(name, str):
                    self._unidentifiedRats.append(name)
                else:
                    raise TypeError(f"Element '{name}' expected to be of type str, got {type(name)}")
        else:
            raise TypeError(f"expected type str, got {type(value)}")

    @property
    def is_open(self) -> bool:
        """
        Bool storing the Rescue's open status.

        - this cannot be named `Rescue.open` as it would shadow the name from the outer scope (bad)

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
        if not value or isinstance(value, str):
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
            # checks to ensure the required fields are present and we have no extras
            if "marked" in value and "reason" in value and "reporter" in value and len(value) == 3:
                self._mark_for_deletion = value
            else:
                log.debug(f"data of value is: {value}")
                raise ValueError("required fields missing and/or garbage data present!")
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
        Sets the rats property directly, it is recommended to use the helper methods to add/remove rats.

        Args:
            value (list): new value for `rats`

        Returns:

        """
        if isinstance(value, list):
            self._rats = value

        else:
            raise TypeError(f"expected type list got {type(value)}")

    def add_rat(self, rat: UUID or str):
        """
        Adds a rat to the rescue.

        Args:
            rat (UUID): rat to add

        Returns:

        """
        if isinstance(rat, str):
            log.debug(f"value was a string with data '{rat}'")
            uuid = UUID(rat)
            log.debug("parsed value into a valid UUID.")
            self._rats.append(Rats(uuid=uuid))
        elif isinstance(rat, UUID):
            self._rats.append(rat)
        else:
            raise TypeError(f"Expected either type str or type UUID. got {type(rat)}")

    @contextmanager
    def change(self):
        """
        Convenience method for making safe attribute changes.

        FIXME: currently just ensures rescue.updated_at is updated.

        TODO: replace with Board context manager once its implemented

        TODO: replace current context manager with a dummy once the Board context manager is a thing.

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
