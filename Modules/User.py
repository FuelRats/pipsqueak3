"""
User.py - Provides a user object

Provides an User object that represents a IRC User

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from typing import Union

from main import MechaClient


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
        # strip fuelrats.com from the end
        leading_data: str = vhost.rsplit(".fuelrats.com")[0]

        # attempt to split the vhost between ident and role
        data_split = leading_data.split('.')

        # sanity check.
        # if the split returns 3+ items, something isn't right here.
        assert len(data_split) <= 2

        if len(data_split) == 1:
            # we have an administrator
            host = f"{data_split[0]}"
        else:
            # standard user
            host = f"{data_split[1]}"

        return f"{host}.fuelrats.com"

    def __init__(self,
                 oper: bool,
                 idle: int,
                 away: bool,
                 away_message: str,
                 identified: bool,
                 secure: bool,
                 account: str,
                 nickname: str,
                 # attributes below this line are nullable
                 username: Union[None, str] = None,
                 hostname: Union[None, str] = None,
                 realname: Union[None, str] = None,
                 server: Union[None, str] = None,
                 server_info: Union[None, str] = None):
        """
        Creates a new IRC user object
        Args:
            oper (bool): is the user an oper
            idle (int): time user is idle for
            away (bool): user's away flag
            away_message (str): user's away message
            username (str): username
            hostname (str): hostname
            realname (str): realname
            identified (bool): NS identification flag
            server (str): server the user belongs to
            server_info (str): server's information string
            secure (bool): Secure connection marker
            account (str): NS identity
            nickname (str): IRC nickname of user

        As a whois entry will not return some fields for users that don't exist,
        Username, hostname, realname, server, and server_info are nullable.

        """
        self._oper: bool = oper
        self._idle: int = idle
        self._away: bool = away
        self._away_message: str = away_message
        self._username: str = username
        self._hostname: str = self.process_vhost(hostname)
        self._realname: str = realname
        self._identified: bool = identified
        self._server: str = server
        self._server_info: str = server_info
        self._secure: bool = secure
        self._account: str = account
        self._nickname: str = nickname

    @property
    def oper(self) -> bool:
        """User's OPER flag, False if they are not an Oper"""
        return self._oper

    @property
    def idle(self) -> int:
        """Idle timer"""
        return self._idle

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
    def server(self) -> str:
        """
        Server user exists on

        (this would be the server the WHOIS was run against)
        """
        return self._server

    @property
    def server_info(self) -> str:
        """Server information"""
        return self._server_info

    @property
    def secure(self) -> bool:
        """Secure connection flag"""
        return self._secure

    @property
    def account(self) -> Union[str, None]:
        """Nickserv account, if applicable"""
        return self._account

    @property
    def nickname(self) -> str:
        return self._nickname

    @classmethod
    async def from_bot(cls, bot: 'MechaClient', nickname: str) -> 'User':
        """
        Creates a user object from a WHOIS reply

        Args:
            bot(MechaClient): MechaClient instance
            nickname(str):  nickname to look up

        Returns:
            User: user object

        Raises:
            ValueError: somehow got an invalid WHOIS response
        """
        data = await bot.whois(nickname)

        # anything less than 7 is not a valid whois reply
        if len(data) < 7:
            raise ValueError("Dict does not contain enough keys")

        # null whois reply, user not found
        if len(data) == 7:
            return cls(oper=data['oper'],
                       idle=data['idle'],
                       away=data['away'],
                       away_message=data['away_message'],
                       identified=data['identified'],
                       secure=data['secure'],
                       account=data['account'],
                       nickname=nickname)

        # full whois reply
        else:
            return cls(oper=data['oper'],
                       idle=data['idle'],
                       away=data['away'],
                       away_message=data['away_message'],
                       identified=data['identified'],
                       secure=data['secure'],
                       account=data['account'],
                       nickname=nickname,
                       username=data['username'],
                       hostname=data['hostname'],
                       realname=data['realname'],
                       server=data['server'],
                       server_info=data['server_info'],
                       )
