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

    @classmethod
    def from_json(cls, data: dict) -> list:
        """
        Parses a Rescue dictionary for quotes
        Args:
            data (dict):

        Returns: list of Quotation objects

        """
        pass


class Rescue(object):
    """
    A rescue
    """

    def __init__(self, case_id: str, client: str, system: str, created_at: datetime = datetime.utcnow(),
                 updated_at: datetime = None, unidentified_rats=None, active=True, quotes: list = None, is_open=True,
                 epic=False, code_red=False, successful=False, title='', first_limpet=None):
        """
        creates a unique rescue\n
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
            first_limpet (str): Id of the rat that got the first limpet
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
        Sets the value of the quotes property to whatever `value` is.
        This should not be set directly outside of case init, rather via `add_quote`


        :param value: value to set quotes to
        :type value: list
        :return: None
        :rtype: None
        """
        if isinstance(value, list):
            self._quotes = value
        else:
            raise ValueError(f"expected type list, got {type(value)}")

    def add_quote(self, message: str, author: str or None = None) -> None:
        """
        Appends a quote to the rescue object\n
        :param message: quoted text to make a quotation
        :type message: str
        :param author: IRC nickname of whoever the quotation is of
        :type author: str
        :return: None
        :rtype: None
        """
        if author:
            self.quotes.append(Quotation(author=author, message=message))
        else:
            self.quotes += Quotation(message=message)

    # TODO: to/from json
    # TODO: track changes
    # TODO: helper method for adding / editing quotes
