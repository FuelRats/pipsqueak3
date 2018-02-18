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

log = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


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
