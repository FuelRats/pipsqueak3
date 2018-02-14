# coding: utf8
"""
permissions.py - Vhost related permissions and whatnot

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from Modules import config
import logging
from functools import wraps

log = logging.getLogger(f"{config.Logging.base_logger}.Permissions")


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

    def __ne__(self, other: 'Permission')->bool:
        return self.level != other.level

    def __le__(self, other: 'Permission')->bool:
        return self.level <= other.level

    def __lt__(self, other: 'Permission')-> bool:
        return self.level < other.level

    def __ge__(self, other: 'Permission')->bool:
        return self.level >= other.level

    def __gt__(self, other: 'Permission')->bool:
        return self.level > other.level


# the uninitiated
RECRUIT = Permission(0, "recruit.fuelrats.com")
# the initiated
RAT = Permission(1, "rat.fuelrats.com")
# The mad hatters
DISPATCH = Permission(2, "dispatch.fuelrats.com")
# Those that oversee the mad house
OVERSEER = Permission(3, 'overseer.fuelrats.com')
# Those that hold the keys
OP = Permission(4, "op.fuelrats.com")
# Those that make all the shiny toys
TECHRAT = Permission(5, 'techrat.fuelrats.com')
# Those that you don't want to upset
NETADMIN = Permission(6, 'netadmin.fuelrats.com')
# Best you don't hear from one of these...
ADMIN = Permission(6, 'admin.fuelrats.com')
# OrangeSheets. why do we have this permission again?
ORANGE = Permission(10, "i.see.all")


def require_permission(permission: Permission, override_message: str or None = None):
    """
    Require an IRC command to be invoked by an authorized user.

    Anything lower than the specified permission will be rejected.
    :param permission: Minimum Permissions level required to invoke command
    :param override_message: Message to display rather than the default if the challange fails
    :return:
    """
    # TODO implement wrapper
    def real_decorator(func):
        log.debug("inside real_decorator")
        log.debug(f"Wrapping a command with permission {permission}")
        # TODO implement require_permission wrapper.

        @wraps(func)
        def guarded(*args, **kwargs):

            func(*args, **kwargs)

        return guarded

    return real_decorator


