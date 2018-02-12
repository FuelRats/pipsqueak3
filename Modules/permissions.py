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
    def __init__(self, level: int, vhost: str, deny_message: str="Access denied."):
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
    # TODO implement other relational operators


class Permissions(enum):
    """
    Permission Enums.
    """
    RECRUIT = Permission(0, "recruit.fuelrats.com")
    RAT = Permission(1, "rat.fuelrats.com")
    DISPATCH = Permission(2, "dispatch.fuelrats.com")
    OVERSEER = Permission(3, 'overseer.fuelrats.com')
    OP = Permission(4, "op.fuelrats.com")
    TECHRAT = Permission(5, 'techrat.fuelrats.com')
    NETADMIN = Permission(6, 'netadmin.fuelrats.com')
    ADMIN = Permission(6, 'admin.fuelrats.com')

def RequirePermission(permission:Permissions, override_message: str or None = None):
    """
    Require an IRC command to be invoked by an authorized user.

    Anything lower than the specifified permission will be rejected.
    :param permission:
    :return:
    """
    # TODO implement wrapper
    pass


