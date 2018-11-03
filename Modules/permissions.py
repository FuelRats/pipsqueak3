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
from typing import Any, Union, Callable, List, Dict, Set

from Modules.context import Context
from config import config

log = logging.getLogger(f"mecha.{__name__}")


class Permission:
    """
    A permission level
    """

    def __init__(self, level: int, vhosts: Set[str],
                 deny_message: str = "Access denied."):
        """
        creates a representation of a permission level required to execute an IRC command

        Args:
            level (Permission): required Permission level
            vhosts (Set[str]): set of vhost strings that fall under this permission level
            deny_message (str): message displayed on message to display if user level < level
                required
        """

        log.debug(f"Created new Permission object with permission {level}")
        self._level = level
        self._vhosts = vhosts
        self._denied_message = deny_message

        _by_vhost.update({vhost: self for vhost in self._vhosts})

    @property
    def level(self) -> int:
        """
        Permission level

        Returns:
            int
        """
        return self._level

    @property
    def vhosts(self) -> Set[str]:
        """
        Registered vhosts that fall under this permission level

        Returns:
            List[str]: list of registered vhosts
        """
        return self._vhosts

    @vhosts.setter
    def vhosts(self, value: Set[str]) -> None:
        """
        Updates the registered vhosts for this permission object

        This also has the side effect of updating the _by_vhost bindings for this object.

        - Items removed from `vhosts` are removed from _by_vhost and
        - Items that are not in `vhosts` already are added to `_by_vhost`

        Args:
            value (List[str]): list of vhosts

        Returns:
            None
        """
        if not isinstance(value, set):
            raise TypeError(f"expected list got {type(value)}")

        # determine which items have been removed
        removed = self.vhosts - value

        # determine which items are new
        added = value - self.vhosts

        # recompute _by_vhost to exclude removed vhosts we have removed
        # ( as there is no bulk-remove method, this avoids a for loop and some function calls )
        all_vhosts = {vhost: permission for vhost, permission in _by_vhost.items() if
                      vhost not in removed}

        # create a dict of new vhosts to register
        new_vhosts = {vhost: self for vhost in added}

        # append new vhosts to the main dict
        all_vhosts.update(new_vhosts)

        # clear the master dict (can't assign directly due to scope)
        _by_vhost.clear()
        # and write it all back to the master
        _by_vhost.update(all_vhosts)

        # oh and update our set whilst we are here <3
        self._vhosts = value

    @classmethod
    def from_dict(cls, data: Dict):
        """
        Parses the provided `data` dict into a Permissions object

        Args:
            data (dict): dictionary to parse

        Returns:
            Permission: initialized permission object

        Examples:
            >>> permission = Permission.from_dict({'vhosts': ['recruits.fuelrats.com'], 'level': 0})
            >>> permission.vhosts
            {'recruits.fuelrats.com'}
            >>> permission.level
            0
        """
        if not isinstance(data, dict):
            raise TypeError(f"expected dict got {type(data)}")

        vhosts = set(data['vhosts'])
        level = data['level']

        return cls(level=level, vhosts=vhosts)

    @property
    def denied_message(self) -> str:
        """
        message displayed when someone's permission level does not exceed the threshold `self.level`

        Returns:
            str: access denied message
        """
        return self._denied_message

    @denied_message.setter
    def denied_message(self, value: str) -> None:
        """
        Set the access denied message

        Args:
            value (str): new message

        Returns:
            None
        """
        if not isinstance(value, str):
            raise TypeError(f"expected type str got {type(value)}")

        self._denied_message = value

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


# mapping between vhosts and permissions
_by_vhost: Dict[str, Permission] = {}

_permissions_dict = config['permissions']
# the uninitiated
RECRUIT = Permission.from_dict(_permissions_dict['recruit'])

# the run of the mill
RAT = Permission(1, _permissions_dict['rat'])

# the overseers of the mad house
OVERSEER = Permission.from_dict(_permissions_dict['overseer'])

# The rats that provide all the shiny toys
TECHRAT = Permission.from_dict(_permissions_dict['techrat'])

# The Administrator.
ADMIN = Permission.from_dict(_permissions_dict['administrator'])


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
        async def guarded(context: Context, *args):
            if context.user.hostname in _by_vhost.keys() \
                    and _by_vhost[context.user.hostname] >= permission:
                return await func(context, *args)
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
        async def guarded(context: Context, *args) -> Any:
            """
            Enforces channel requirement

            Args:
                context (Context): IRC command context

            Returns:
                Any: whatever the called function returned
            """
            if context.channel is not None:
                return await wrapped(context, *args)
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
        async def guarded(context: Context, *args) -> Any:
            """
            Enforces channel requirement

            Args:
                context (Context): IRC command context

            Returns:
                Any: whatever the called function returned
            """
            if context.channel is None:
                return await wrapped(context, *args)
            else:
                log.debug(f"channel was None, enforcing channel requirement...")
                await context.reply(message)

        return guarded

    # if the form is @require_dm(*args, **kwargs) we need to call and return real_decorator
    # otherwise we can just return real_decorator directly
    return real_decorator(func) if func else real_decorator
