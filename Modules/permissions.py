"""
permissions.py - Vhost related permissions and whatnot

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import logging
from functools import wraps

import config

log = logging.getLogger(f"{config.Logging.base_logger}.Permissions")


class Permission:
    """
    A permission level
    """
    def __init__(self, level: int, vhost: str,
                 deny_message: str="Access denied."):
        """
        Permission required to execute a command
        :param level: Relative permissions level
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

    def __ne__(self, other: 'Permission') -> bool:
        return self.level != other.level

    def __le__(self, other: 'Permission') -> bool:
        return self.level <= other.level

    def __lt__(self, other: 'Permission') -> bool:
        return self.level < other.level

    def __ge__(self, other: 'Permission') -> bool:
        return self.level >= other.level

    def __gt__(self, other: 'Permission') -> bool:
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

_by_vhost = {
    "recruit.fuelrats.com": RECRUIT,
    "rat.fuelrats.com": RAT,
    "dispatch.fuelrats.com": DISPATCH,
    "overseer.fuelrats.com": OVERSEER,
    "op.fuelrats.com": OP,
    "techrat.fuelrats.com": TECHRAT,
    "netadmin.fuelrats.com": NETADMIN,
    "admin.fuelrats.com": ADMIN,
    "i.see.all": ORANGE
}


def require_permission(permission: Permission,
                       override_message: str or None=None):
    """
    Require an IRC command to be invoked by an authorized user.

    Anything lower than the specified permission will be rejected.

    Args:
        permission (Permission): Minimum Permissions level required to invoke
            command
        override_message (str): Message to display rather than the default if
            the challenge fails

    Returns:

    """

    def real_decorator(func):
        log.debug("inside real_decorator")
        log.debug(f"Wrapping a command with permission {permission}")
        # TODO implement require_permission wrapper.

        @wraps(func)
        async def guarded(bot, trigger, words, words_eol):
            if trigger.identified and trigger.hostname in _by_vhost.keys() \
                    and _by_vhost[trigger.hostname] >= permission:
                try:
                    # This works if we're the bottommost decorator
                    # (calling the command function directly)
                    return await func(bot, trigger)
                except TypeError:
                    # Otherwise, we're giving all the things to the underlying
                    #  wrapper (be it from parametrize or sth)
                    return await func(bot, trigger, words, words_eol)
            else:
                await trigger.reply(override_message if override_message
                                    else permission.denied_message)

        return guarded
    return real_decorator
