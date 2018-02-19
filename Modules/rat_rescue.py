"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import logging
from datetime import datetime

import config
from Modules.trigger import Trigger

log = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


class Quotes(object):
    """
    A quotes object, element of Rescue

    """

    def __init__(self, message: str, author="Mecha", created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                 last_author="Mecha"):
        """
        Creates a new Quotes object\n
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
        Recorded message
        :return: message
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, value) -> None:
        """
        Sets the message property
        :param value: value to set
        :type value: str
        :return: None
        :rtype: None
        """
        self._message = value

    @property
    def author(self) -> str:
        """
        Original author of message ( READ ONLY )
        :return: author
        :rtype: str
        """
        return self._author

    @property
    def created_at(self) -> datetime:
        """
        When the case was created
        :return: time of creation
        :rtype: datetime
        """
        return self._created_at

    @property
    def updated_at(self):
        """
        When the quote was last modified
        :return: modify time
        :rtype: datetime
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value):
        if isinstance(value, datetime):
            self._updated_at = value
        else:
            f"Expected string got {type(value)}"

    @property
    def last_author(self):
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
        :param event_trigger: who triggered the modification
        :type event_trigger: trigger
        :param message: message to write
        :type: str
        :return: None
        :rtype: None
        """
        self._message = message
        self._updated_at = datetime.utcnow()
        self._last_author = event_trigger.nickname

    @classmethod
    def new(cls, rescue: 'Rescue', message: str, author: str = "mecha"):
        """
        Helper method: Add a new quote to an existing rescue\n
        :param rescue: Rescue object to append quotes to
        :param message: quote to record
        :type message: str
        :param author: Who made the associated quote
        :type author: str
        :return:
        :rtype:
        """

        rescue.quotes.append(cls(message=message, author=author))


class Rescue(object):
    """
    A rescue
    """

    def __init__(self, case_id: str, client: str, system: str, created_at: datetime = datetime.utcnow(),
                 updated_at: datetime = None, unidentified_rats=None, active=True, quotes: list = None, is_open=True,
                 epic=False, code_red=False, successful=False, title='', first_limpet=None):
        """
        A unique rescue\n
        :param case_id: API id of rescue
        :type case_id: str
        :param client: The client's Commander name
        :type client: str
        :param system: The reported system for the rescue
        :type system: str
        :param created_at: Time the Rescue was first created ( READ ONLY once set)
        :type created_at: datetime
        :param updated_at: Last time the rescue was modified
        :type updated_at: datetime
        :param unidentified_rats: Assigned but unidentified rats
        :type unidentified_rats: list
        :param active: Bool determining if the case is marked as active
        :type active: bool
        :param quotes: Associated quotes for rescue
        :type quotes: list
        :param is_open: whether the case is marked as open
        :type is_open: bool
        :param epic: Is the rescue an Epic (NOT IMPLEMENTED YET)
        :type epic: bool
        :param code_red: is the rescue Code Red
        :type code_red: bool
        :param successful: was the rescue a success?
        :type successful: bool
        :param title: title for rescue, if any
        :type title: str
        :param first_limpet: Rat ID of the first-limpet
        :type first_limpet: str
        """
        self._createdAt: datetime = created_at
        self._updatedAt: datetime = updated_at
        self._id: str = case_id
        self._client: str = client
        self._irc_nick: str = self._client.replace(" ", "_")
        self._unidentifiedRats = unidentified_rats
        self._system: str = system.upper()
        self._active: bool = active
        self._quotes: list = quotes if quotes else []
        self._open: bool = is_open
        self._epic: bool = epic
        self._codeRed: bool = code_red
        self._successful: bool = successful
        self._title: str = title
        self._firstLimpet: str = first_limpet

    @property
    def case_id(self) -> str:
        """
        The API Id of the rescue. This field is READ ONLY\n
        :return: api ID
        :rtype: str
        """
        return self._id

    @property
    def client(self) -> str:
        """
        The client the rescue is for\n
        :return: the client
        :rtype: str
        """
        return self._client

    @client.setter
    def client(self, name) -> None:
        """
        Set the client's Commander name\n
        :param name: the client's Commander name
        :type name: str
        :return: None
        :rtype: None
        """
        self._client = name

    @property
    def created_at(self) -> datetime:
        """
        Case creation time, this property is readonly.
        It can only be set during Rescue creation\n
        :return: creation date
        :rtype: datetime
        """
        return self._createdAt

    @property
    def system(self) -> str:
        """
        The clients system\n
        :return: the system name
        :rtype: str
        """
        return self._system

    @system.setter
    def system(self, value: str):
        """
        Set the system name
        :param value: value to set the system to\n
        :type value: str
        :return:
        :rtype:
        """
        # for API v2.1 compatibility reasons we cast to upper case
        self._system = value.upper()

    @property
    def active(self) -> bool:
        """
        Property storing the active state of the rescue\n
        :return: is the case marked active?
        :rtype: bool
        """
        return self._active

    @active.setter
    def active(self, value):
        if isinstance(value, bool):
            self._active = value
        else:
            raise ValueError(f"expected bool, got type {type(value)}")

    @property
    def quotes(self) -> list:
        """
        Quotes associated with this rescue\n
        :return: list of quotes
        :rtype: list
        """
        return self._quotes

    @quotes.setter
    def quotes(self, value):
        """
        Sets the value of the quotes property to whatever `value` is\n
        :param value: value to set quotes to
        :type value: list
        :return: None
        :rtype: None
        """
        if isinstance(value, list):
            self._quotes = value
        else:
            raise ValueError(f"expected type list, got {type(value)}")

    def add_quote(self, value: dict) -> None:
        """
        Appends a quote to the rescue object\n
        :param value: quote data to append
        :type value: dict
        :return: None
        :rtype: None
        """
        self.quotes.append(value)
    # TODO: to/from json
    # TODO: track changes
    # TODO: helper method for adding / editing quotes
