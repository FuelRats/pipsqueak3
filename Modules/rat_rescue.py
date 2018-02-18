"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import logging
import config
from datetime import datetime
log = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


class Rescue(object):
    """
    A unique rescue
    """
    def __init__(self, case_id: str, client: str, system: str, created_at: datetime=None, updated_at: datetime=None,
                 unidentified_rats=None, active=True, quotes: list = None, is_open=True, epic=False, code_red=False,
                 successful=False, title='', first_limpet=None):
        """
        Create a new rescue
        """
        self._createdAt: datetime = created_at
        self._updatedAt: datetime = updated_at
        self._id: str = case_id
        self._client: str = client
        self._irc_nick: str = self._client.replace(" ", "_")
        self._unidentifiedRats = unidentified_rats
        self._system: str = system.upper()
        self._active: bool = active
        self._quotes: list = quotes
        self._open: bool = is_open
        self._epic: bool = epic
        self._codeRed: bool = code_red
        self._successful: bool = successful
        self._title: str = title
        self._firstLimpet: str = first_limpet

    @property
    def client(self)->str:
        """
        The client the rescue is for\n
        :return: the client
        :rtype: str
        """
        return self._client

    @client.setter
    def client(self, name)->None:
        """
        Set the client's Commander name\n
        :param name: the client's Commander name
        :type name: str
        :return: None
        :rtype: None
        """
        self.client = name

    @property
    def created_at(self)-> datetime:
        """
        Case creation time, this property is readonly.
        It can only be set during Rescue creation\n
        :return: creation date
        :rtype: datetime
        """
        return self._createdAt

    @property
    def system(self)->str:
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

    @system.getter
    def system(self)->str:
        """
        get the system name\n
        :return: the system name
        :rtype: str
        """
        return self._system

    # TODO: to/from json
    # TODO: track changes
