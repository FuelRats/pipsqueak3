"""
user.py - User objects main program

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
        """
        Create a new IRC User representation

        Args:
            realname (str): real name
            hostname (str): hostmask
            nickname (str):  nickname
            username (str): username
            target (str):  ?
            away (bool): user's away status
            account (?): ?
            identified (bool): user identification status against IRC services
        """
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
        """nickname"""
        return self._nickname

    @property
    def username(self) -> str:
        """username"""
        return self._nickname

    @property
    def identified(self) -> bool:
        """is user identified?"""
        return self._identified

    @property
    def away(self) -> bool:
        """is the user marked away?"""
        return self._away

    @property
    def target(self) -> str:
        """FIXME: no idea what this field is for"""
        return self._target

    @property
    def account(self):
        # FIXME: no idea what this field is for
        return self._account
