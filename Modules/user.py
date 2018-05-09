"""
user.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""


class User(object):
    """Represents an IRC user"""

    def __init__(self,
                 realname: str,
                 hostname: str,
                 nickname: str,
                 username: str,
                 target,
                 away: bool,
                 account,
                 identified: bool = False,
                 ):
        """Create a new user"""
        self._realname: str = realname
        self._hostname: str = hostname
        self._nickname: str = nickname
        self._username: str = username
        self._identified: bool = identified
        self._away: bool = away
        self._target = target
        self._account = account

    @property
    def realname(self) -> str:
        """The user's real name"""
        return self._realname

    @property
    def hostname(self) -> str:
        """The users hostname"""
        return self._hostname

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def username(self) -> str:
        return self._nickname

    @property
    def identified(self) -> bool:
        return self._identified

    @property
    def away(self) -> bool:
        return self._away

    @property
    def target(self):
        return self._target

    @property
    def account(self):
        return self._account
