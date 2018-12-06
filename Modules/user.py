"""
User.py - Provides a user object

Provides an User object that represents a IRC User

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from functools import reduce
from operator import xor
from typing import Union, Optional

from pydle import BasicClient


class User(object):
    """
    Represents an IRC user
    """

    @classmethod
    def process_vhost(cls, vhost: Union[str, None]) -> Union[None, str]:
        """
        Refines a raw vhost into `{role}.fuelrats.com`

        Args:
            vhost (str): raw host string

        Returns:
            str : refined vhost
            None: invalid vhost, raw vhost was None
        """
        # sanity check
        if vhost is None:
            return None
        # lets see if its orange, because orange has a special vhost.
        if vhost == "i.see.all":
            return vhost
        # sanity / security check
        if not vhost.endswith(".fuelrats.com"):
            return None

        # identify the role
        host = vhost.rsplit(".", 3)[-3]

        # return the corresponding vhost
        return f"{host}.fuelrats.com"

    def __init__(self,
                 away: bool,
                 away_message: Optional[str],
                 identified: bool,
                 account: str,
                 nickname: str,
                 # attributes below this line are nullable
                 username: Optional[str] = None,
                 hostname: Optional[str] = None,
                 realname: Optional[str] = None,

                 ):
        """
        Creates a new IRC user object
        Args:
            idle (int): time user is idle for
            away (bool): user's away flag
            away_message (str): user's away message
            username (str): username
            hostname (str): hostname
            realname (str): realname
            identified (bool): NS identification flag
            account (str): NS identity
            nickname (str): IRC nickname of user

        As a whois entry will not return some fields for users that don't exist,
        Username, hostname, realname, server, and server_info are nullable.

        """
        self._away: bool = away
        self._away_message: str = away_message
        self._username: str = username
        self._hostname: str = self.process_vhost(hostname)
        self._realname: str = realname
        self._identified: bool = identified

        self._account: str = account
        self._nickname: str = nickname

        self._hash = None

    @property
    def away(self) -> bool:
        """User's away flag"""
        return self._away

    @property
    def away_message(self) -> Union[None, str]:
        """
        User's away message, if it exists. otherwise None
        """
        return self._away_message

    @property
    def username(self) -> str:
        """Username"""
        return self._username

    @property
    def hostname(self) -> str:
        """Hostname"""
        return self._hostname

    @property
    def realname(self) -> str:
        """User's set realname"""
        return self._realname

    @property
    def identified(self) -> bool:
        """Nickserv ident flag"""
        return self._identified

    @property
    def account(self) -> Union[str, None]:
        """Nickserv account, if applicable"""
        return self._account

    @property
    def nickname(self) -> str:
        """Nickname"""
        return self._nickname

    @classmethod
    async def from_pydle(cls, bot: BasicClient, nickname: str) -> Optional['User']:
        """
        Returns a user object from pydle's backend

        Args:
            bot (BasicClient): Mechaclient instance
            nickname (str): nickname of user

        Returns:
            User: found user
            None: user not found
        """
        # fetch the user object from
        data = bot.users.get(nickname.casefold(), None)

        # if we got a object back

        if data:
            return cls(**data)

    def __eq__(self, other) -> bool:
        """
        Check equality

        Args:
            other (User):

        Returns:
            bool
        """
        if not isinstance(other, User):
            return NotImplemented

        conditions = [

            self.away == other.away,
            self.away_message == other.away_message,
            self.username == other.username,
            self.hostname == other.hostname,
            self.identified == other.identified,
            self.account == other.account,
            self.nickname == other.nickname
        ]
        return all(conditions)

    def __hash__(self) -> int:
        if self._hash is None:
            attrs = (self.oper, self.idle, self.away, self.away_message, self.username,
                     self.hostname, self.identified, self.server, self.server_info, self.secure,
                     self.account, self.nickname)

            # borrowed hashing mechanism from the old Trigger object
            self._hash = reduce(xor, map(hash, attrs))
        return self._hash
