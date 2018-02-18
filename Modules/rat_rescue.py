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
log = logging.getLogger(f"{config.Logging.base_logger}.{__name__}")


class Rescue(object):
    """
    A unique rescue
    """
    def __init__(self, created_at, updated_at, case_id, client, unidentified_rats, system, active=True,
                 quotes: list = None, is_open=True, epic=False, code_red=False, successful=False, title='',
                 first_limpet=None):
        """
        Create a new rescue
        """
        self.createdAt = created_at
        self.updatedAt = updated_at
        self.id = case_id
        self.client = client
        self.unidentifiedRats = unidentified_rats
        self.system = system
        self.active = active
        self.quotes = quotes
        self.open = is_open
        self.epic = epic
        self.codeRed = code_red
        self.successful = successful
        self.title = title
        self.firstLimpet = first_limpet

    @property
    def system(self)->str:
        """
        The clients system\n
        :return: the system name
        :rtype: str
        """
        return self.system

    @system.setter
    def system(self, value: str):
        """
        Set the system
        :param value: value to set the system to\n
        :type value: str
        :return:
        :rtype:
        """
        # for API v2.1 compatibility reasons we cast to upper case
        self.system = value.upper()

    @system.getter
    def system(self)->str:
        """
        get the system name\n
        :return: the system name
        :rtype: str
        """
        return self.system

    # TODO: to/from json
    # TODO: track changes
