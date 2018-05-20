"""
user.py - User objects main program

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import logging
from typing import Union

from pydle import BasicClient

import config
from Modules import permissions
from Modules.permissions import Permission

LOG = logging.getLogger(f"{config.Logging.base_logger}.Permissions")


class User(object):
    """Represents an IRC user"""

    def __init__(self,
                 realname: str,
                 hostname: str,
                 nickname: str,
                 username: str,
                 away: bool,
                 away_message: Union[str, None],
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
            away_message(str): user's away message
            account (?): ?
            identified (bool): user identification status against IRC services

        """
        self._realname: str = realname
        self._hostname: str = hostname
        self._nickname: str = nickname
        self._username: str = username
        self._identified: bool = identified
        self._away: bool = away
        self._account: str = account
        self._permission_level: Union[None, Permission] = None
        self._away_message: Union[str, None] = away_message
        # sets the permission based on the hostmask
        # which requires stripping the username and the leading period
        try:
            # FIXME: access to protected member
            # loop over every known vhost
            for key, value in permissions._by_vhost.items():
                # if a vhost matches, and the user is identified
                if hostname.endswith(key) and identified is True:
                    self._permission_level = value
        except KeyError:
            # means the user didn't have  a valid hostmask, ignore it.
            LOG.debug(f"no matching permission for hostname {hostname}")
            pass

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
        return self._username

    @property
    def identified(self) -> bool:
        """is user identified?"""
        return self._identified

    @property
    def away(self) -> bool:
        """is the user marked away?"""
        return self._away

    @property
    def away_message(self):
        return self._away_message
    @property
    def account(self) -> Union[str, None]:
        """Users nickserv account, None if not identified"""
        return self._account

    @property
    def permission_level(self) -> Union[None, Permission]:
        """
        IRC permission level for the user,
            this property is Derrived from the hostmask.
        Returns:
            Permission or None
        """
        return self._permission_level

    @classmethod
    async def from_bot(cls, bot: BasicClient, nickname: str) -> Union['User', None]:
        """
        Initalizes a new User from their IRC presence

        Returns:
            User: user created from IRC presence
        """
        # fetch the user data from their IRC observed presence
        irc_user = await bot.whois(nickname)
        my_user = None
        if irc_user is None:
            raise ValueError(f"unable to find nickname {nickname}")
        else:
            # and create an instance
            my_user = cls(realname=irc_user['realname'],
                          username=irc_user["username"],
                          hostname=irc_user["hostname"],
                          nickname=irc_user["nickname"],
                          away=irc_user["away"],
                          account=irc_user["account"],
                          identified=irc_user["identified"],
                          away_message=irc_user["away_message"]
                          )

        return my_user
