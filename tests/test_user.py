"""
test_user.py - Test suite for User

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import pytest

from Modules import permissions
from Modules.user import User


@pytest.mark.parametrize("prop", ["realname", "hostname", "username", "away",
                                  "account", "identified"])
def test_read_only(user_fx: User, prop: str):
    """ verifies all properties on the User object are read only"""
    # one downside to this approach is new attributes need to be added manually :/
    with pytest.raises(AttributeError):
        user_fx.__setattr__(prop, 42)


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_data", (
        ({'oper': False,
          'idle': 0,
          'away': False,
          'away_message': None,
          'username': 'theunkn0wn',
          'hostname': 'theunkn0wn1.techrat.fuelrats.com',
          'realname': 'unknown',
          'identified': True,
          'channels': {'~@#unkn0wndev'},
          'server': 'irc.eu.fuelrats.com',
          'server_info': 'Fuel Rats IRC Server',
          'secure': True,
          'account': 'theunkn0wn1[PC]'}, permissions.TECHRAT),))
async def test_from_irc(bot_fx, monkeypatch, mock_data):
    async def mock_return(*args):
        return mock_data[0]

    monkeypatch.setattr("tests.mock_bot.MockBot.whois", mock_return)
    user: User = await User.from_bot(bot_fx, mock_data[0]['username'])
    assert mock_data[0]['username'] == user.username
    assert mock_data[0]['away'] == user.away
    assert mock_data[0]['realname'] == user.realname
    assert mock_data[0]['hostname'] == user.hostname
    assert mock_data[0]['account'] == user.account
    assert mock_data[0]['identified'] == user.identified

