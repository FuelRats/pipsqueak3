"""
permissions.py - Vhost related permissions and whatnot

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import logging
from functools import wraps
from typing import Any, Union, Callable

from Modules.context import Context

log = logging.getLogger(f"mecha.{__name__}")


class Permission:
    """
    A permission level
    """

    def __init__(self, level: int, vhost: str,
                 deny_message: str = "Access denied."):
        """
        Permission required to execute a command
        :param level: Relative permissions level
        :param vhost: associated vhost
        :param deny_message: message to display if user level < level required
        :return:
        """
        log.debug(f"Created new Permission object with permission {level}")
        self._level = level
        self._vhost = vhost
        self._denied_message = deny_message

    level = property(lambda self: self._level)
    vhost = property(lambda self: self._vhost)
    denied_message = property(lambda self: self._denied_message)

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

    def __hash__(self):
        return hash(self.level)


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
                       override_message: str or None = None):
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
        log.debug("Inside the real_decorator")
        log.debug(f"Wrapping a command with permission {permission}")

        @wraps(func)
        async def guarded(context: Context):
            if context.user.identified and context.user.hostname in _by_vhost.keys() \
                    and _by_vhost[context.user.hostname] >= permission:
                return await func(context)
            else:
                await context.reply(override_message if override_message
                                    else permission.denied_message)

        return guarded

    return real_decorator


def require_channel(func: Union[str, Callable] = None,
                    message: str = "This command must be invoked in a channel."):
    """
    Require the wrapped IRC command to be invoked in a channel context.

    Args:
        func(Union[str, Callable]): wrapped function / message
        message(str): message to display on check fail

    Usage:
        >>> @require_channel
        ... async def my_command(context: Context):
        ...     pass

        >>> @require_channel("access denied.")
        ... async def my_command(context: Context):
        ...     pass

        >>> @require_channel(message="access denied.")
        ... async def my_command(context: Context):
        ...     pass
    """
    # form of @decorator("message") and @decorator(message=str)
    if isinstance(func, str):
        message = func

    # direct decoration
    if not callable(func):
        func = None

    def real_decorator(wrapped):
        """
        The function decorator that implements the `guarded` local

        this wrapper is necessary to prevent coro object not callable in
        @require_channel(*args, **kwargs) form

        Args:
            wrapped (function): the function being decorated

        Returns:
            callable: guarded function
        """

        @wraps(wrapped)
        async def guarded(context: Context) -> Any:
            """
            Enforces channel requirement

            Args:
                context (Context): IRC command context

            Returns:
                Any: whatever the called function returned
            """
            if context.channel is not None:
                return await wrapped(context)
            else:
                log.debug(f"channel was None, enforcing channel requirement...")
                await context.reply(message)

        return guarded

    # if the form is @require_decorator(*args, **kwargs) we need to call and return real_decorator
    # otherwise we can just return real_decorator directly
    return real_decorator(func) if func else real_decorator


# def require_dm(message: str = "command {cmd} must be invoked in a private message."):

def require_dm(func: Union[str, Callable] = None,
               message: str = "This command must be invoked in a channel."):
    """
    Require the wrapped IRC command to be invoked in a DM context.

    Args:
        func(Callable): wrapped function / access denied string override
        message(str): access denied string

    Usage:
        >>> @require_dm
        ... async def my_command(context: Context):
        ...     pass

        >>> @require_dm("access denied.")
        ... async def my_command(context: Context):
        ...     pass

        >>> @require_dm(message="access denied.")
        ... async def my_command(context: Context):
        ...     pass
    """
    # form of @decorator("message") and @decorator(message=str)
    if isinstance(func, str):
        message = func

    # direct decoration
    if not callable(func):
        func = None

    def real_decorator(wrapped):
        """
        The function decorator that implements the `guarded` local


        this wrapper is necessary to prevent coro object not callable in
        @require_dm(*args, **kwargs) form

        Args:
            wrapped (function): the function being decorated

        Returns:
            callable: guarded function
        """

        @wraps(wrapped)
        async def guarded(context: Context) -> Any:
            """
            Enforces channel requirement

            Args:
                context (Context): IRC command context

            Returns:
                Any: whatever the called function returned
            """
            if context.channel is None:
                return await wrapped(context)
            else:
                log.debug(f"channel was None, enforcing channel requirement...")
                await context.reply(message)

        return guarded

    # if the form is @require_dm(*args, **kwargs) we need to call and return real_decorator
    # otherwise we can just return real_decorator directly
    return real_decorator(func) if func else real_decorator
