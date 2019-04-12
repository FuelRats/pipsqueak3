"""
User.py - Provides a user object

Provides an User object that represents a IRC User

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from __future__ import annotations  # enable forward-references

from dataclasses import dataclass
from typing import Union, Optional

from pydle import BasicClient


@dataclass(frozen=True)
class User:
    """
    Represents an IRC user
    """
    away: bool
    away_message: Optional[str]
    username: str
    hostname: str
    realname: str
    identified: bool
    account: Optional[str]
    nickname: str

    @classmethod
    async def from_pydle(cls, bot: BasicClient, nickname: str) -> Optional[User]:
        """
        Returns a user object from pydle's backend

        Args:
            bot (BasicClient): Mechaclient instance
            nickname (str): nickname of user

        Returns:
            User: found user
            None: user not found
        """
        # fetch the user object from pydle
        data = bot.users.get(nickname.casefold(), None)

        # if we got a object back
        if data:
            return cls(**data)

    @classmethod
    def process_vhost(cls, vhost: Union[str, None]) -> Optional[str]:
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
