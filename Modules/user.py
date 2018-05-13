"""
user.py - User objects main program

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from pydle import BasicClient


class User(object):
    """Represents an IRC user"""

    def __init__(self,
                 realname: str,
                 hostname: str,
                 nickname: str,
                 username: str,
                 away: bool,
                 account: str,
                 identified: bool = False,
                 ):
        """
        Create a new IRC User representation

        Args:
            realname (str): real name
            hostname (str): hostmask
            nickname (str):  nickname
            username (str): username
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
    def account(self):
        # FIXME: no idea what this field is for
        return self._account

    @classmethod
    async def from_bot(cls, bot: BasicClient, nickname: str) -> 'User':
        """
        Initalizes a new User from their IRC presence

        Returns:
            User: user created from IRC presence
        """
        # fetch the user data from their IRC observed presence
        irc_user = await bot.whois(nickname)
        # and create an instance
        my_user = cls(realname=irc_user['realname'],
                      username=irc_user["username"],
                      hostname=irc_user["hostname"],
                      nickname=irc_user["username"],
                      away=irc_user["away"],
                      account=irc_user["account"],
                      identified=irc_user["identified"]
                      )

        return my_user
