"""
test_user.py - test suite for `Modules.User`

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import pytest

from Modules.user import User
pytestmark = pytest.mark.user

@pytest.mark.parametrize("expected_host", [
    "recruit.fuelrats.com",
    "rat.fuelrats.com",
    "dispatch.fuelrats.com",
    "overseer.fuelrats.com",
    "op.fuelrats.com",
    "techrat.fuelrats.com",
    "netadmin.fuelrats.com",
    "admin.fuelrats.com",
])
@pytest.mark.parametrize("prefix", ["potato.", "Orbital.", ""])
def test_process_vhost(prefix: str, expected_host: str):
    """
    Asserts vhost processing functions as expected
    """
    mixed_host = f"{prefix}{expected_host}"
    assert User.process_vhost(mixed_host) == expected_host


def test_process_vhost_orange():
    """
    Asserts vhost processing works for Orange, as he has a special vhost
    (that can't be tested in the parametrize)
    """
    assert User.process_vhost("i.see.all") == "i.see.all"


@pytest.mark.parametrize("garbage", ("i.see.none", "furats.com", "not.so.clever.fuelrats.com.com",
                                     "Clk-FFFFAA3F.customer.potato.net", None))
def test_process_vhost_garbage(garbage: str):
    """
    Verifies result of throwing garbage at `User.process_vhost()`
    """
    assert User.process_vhost(garbage) is None


@pytest.mark.parametrize("data", (
        {'oper': False,
         'idle': 0,
         'away': False,
         'away_message': None,
         'username': 'White',
         'hostname': 'recruit.fuelrats.com',
         'realname': 'WhiteStrips',
         'identified': False,
         'server': 'irc.fuelrats.com',
         'server_info': 'Fuel Rat IRC Server',
         'secure': True,
         'account': 'WhiteStrips'},
        {'oper': True,
         'idle': 0,
         'away': False,
         'away_message': None,
         'username': 'AwesomeAdmin',
         'hostname': 'admin.fuelrats.com',
         'realname': 'you know',
         'identified': True,
         'server': 'irc.fuelrats.com',
         'server_info': 'Fuel Rat IRC Server',
         'secure': True,
         'account': 'AwesomeAdmin'}
))
def test_user_constructor(data: dict):
    """
    Tests the User constructor
    """
    my_user = User(oper=data['oper'],
                   idle=data['idle'],
                   away=data['away'],
                   away_message=data['away_message'],
                   identified=data['identified'],
                   secure=data['secure'],
                   account=data['account'],
                   nickname="unit_test",
                   username=data['username'],
                   hostname=data['hostname'],
                   realname=data['realname'],
                   server=data['server'],
                   server_info=data['server_info'],
                   )

    assert data['oper'] == my_user.oper
    assert data['idle'] == my_user.idle
    assert data['away'] == my_user.away
    assert data['away_message'] == my_user.away_message
    assert data['identified'] == my_user.identified
    assert data['secure'] == my_user.secure
    assert data['account'] == my_user.account
    assert "unit_test" == my_user.nickname
    assert data['hostname'] == my_user.hostname
    assert data['username'] == my_user.username
    assert data['realname'] == my_user.realname
    assert data['server'] == my_user.server
    assert data['server_info'] == my_user.server_info


@pytest.mark.asyncio
async def test_user_from_whois_existing_user(bot_fx):
    """
    verifies building a User from a full IRC reply when said user exists
    """

    my_user = await User.from_whois(bot_fx, "some_recruit")

    data = bot_fx.users['some_recruit']
    assert data['oper'] == my_user.oper
    assert data['idle'] == my_user.idle
    assert data['away'] == my_user.away
    assert data['away_message'] == my_user.away_message
    assert data['identified'] == my_user.identified
    assert data['secure'] == my_user.secure
    assert data['account'] == my_user.account
    assert "some_recruit" == my_user.nickname
    assert data['hostname'] == my_user.hostname
    assert data['username'] == my_user.username
    assert data['realname'] == my_user.realname
    assert data['server'] == my_user.server
    assert data['server_info'] == my_user.server_info


@pytest.mark.asyncio
async def test_user_from_whois_miss(monkeypatch, bot_fx):
    async def mock_whois(*args):
        raise AttributeError("because pydle")

    # patch in the exception raiser
    monkeypatch.setattr("tests.mock_bot.MockBot.whois", mock_whois)

    ret = await User.from_whois(bot_fx, "snafu")
    assert ret is None


@pytest.mark.asyncio
async def test_user_from_whois_malformed_return(monkeypatch, bot_fx):
    async def mock_return(*args) -> dict:
        """returns a malformed dict"""
        return {}

    monkeypatch.setattr("tests.mock_bot.MockBot.whois", mock_return)
    with pytest.raises(ValueError):
        await User.from_whois(bot_fx, "FUBAR")


@pytest.mark.asyncio
@pytest.mark.parametrize("data", (
        {'oper': False,
         'idle': 0,
         'away': False,
         'away_message': None,
         'username': 'White',
         'hostname': 'recruit.fuelrats.com',
         'realname': 'WhiteStrips',
         'identified': False,
         'server': 'irc.fuelrats.com',
         'server_info': 'Fuel Rat IRC Server',
         'secure': True,
         'account': 'WhiteStrips'},
        {'oper': True,
         'idle': 0,
         'away': False,
         'away_message': None,
         'username': 'AwesomeAdmin',
         'hostname': 'admin.fuelrats.com',
         'realname': 'you know',
         'identified': True,
         'server': 'irc.fuelrats.com',
         'server_info': 'Fuel Rat IRC Server',
         'secure': True,
         'account': 'AwesomeAdmin'}
))
async def test_user_eq(data: dict, monkeypatch, bot_fx):
    """
    verifies building a User from a full IRC reply when said user exists
    """

    async def mock_return(*args) -> dict:
        return data

    monkeypatch.setattr("tests.mock_bot.MockBot.whois", mock_return)

    user_alpha = await User.from_whois(bot_fx, "unit_test")
    user_beta = User(data['oper'],
                     data['idle'],
                     data['away'],
                     data['away_message'],
                     data['identified'],
                     data['secure'],
                     data['account'],
                     "unit_test",
                     data['username'],
                     data['hostname'],
                     data['realname'],
                     data['server'],
                     data['server_info'])

    assert user_alpha == user_beta
