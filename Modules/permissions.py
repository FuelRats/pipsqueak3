# coding: utf8
"""
permissions.py - Vhost related permissions and whatnot

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from Modules import constants
import logging
import enum

log = logging.getLogger(f"{constants.base_logger}.Permissions")


class Permission:
    def __index__(self, level: int, vhost: str, deny_message: str="Access denied."):
        """
        Permission required to execute a command
        :param level: Relitive permissions level
        :param vhost: associated vhost
        :param deny_message: message to display if user level < level required
        :return:
        """
        log.debug(f"created new Permission object with permission level")
        self.level = level
        self.vhost = vhost
        self.denied_message = deny_message

    def __eq__(self, other: 'Permission') -> bool:
        return self.level == other.level

    def __le__(self, other: 'Permission')->bool:
        return self.level < other.level

    def __ne__(self, other: 'Permission')->bool:
        return self.level != other.level



