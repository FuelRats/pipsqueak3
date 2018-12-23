"""
test_permissions.py

Tests for the permissions module

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from itertools import product
from typing import Set

import pytest

import Modules.rat_command as Commands
from Modules import permissions, context
from Modules.permissions import require_permission, require_channel, require_dm, Permission

pytestsmark = pytest.mark.permissions


@pytest.fixture
def Setup_fx(bot_fx):
    """Sets up the test environment"""
    Commands._flush()


@pytest.fixture
def restricted_command_fx(async_callable_fx, Setup_fx):
    restricted = require_permission(permissions.OVERSEER)(async_callable_fx)

    Commands.command("restricted")(restricted)
    return async_callable_fx


...


def test_permission_greater():
    """
    Tests if Permission_a > Permission_b functions correctly.
    :return:
    """
    assert permissions.RAT > permissions.RECRUIT
    assert permissions.ADMIN > permissions.RAT
    assert not permissions.RAT > permissions.TECHRAT


def test_permission_lesser():
    """
    Tests if Permission_a < Permission_b correctly.
    :return:
    """
    assert permissions.RECRUIT < permissions.RAT
    assert permissions.RAT < permissions.TECHRAT
    assert permissions.OVERSEER < permissions.TECHRAT


def test_permission_le():
    """
    Tests if Permission_a <= Permission_b correctly.
    :return:
    """
    assert permissions.ADMIN <= permissions.ADMIN
    assert not permissions.ADMIN <= permissions.RAT
    assert permissions.OVERSEER <= permissions.ADMIN
    assert not permissions.ADMIN <= permissions.OVERSEER


def test_permission_ge():
    """
    Tests if Permission_a <= Permission_b correctly.
    :return:
    """
    assert permissions.ADMIN >= permissions.ADMIN
    assert permissions.ADMIN >= permissions.RAT
    assert not permissions.RAT >= permissions.OVERSEER


def test_permission_equal():
    """
    Verifies that Permission_a == Permission_b
    :return:
    """
    assert permissions.RAT == permissions.RAT
    assert permissions.TECHRAT == permissions.TECHRAT
    assert permissions.ADMIN == permissions.ADMIN


def test_permission_not_equal():
    """
    Verifies that Permission_a != Permission_b
    :return:
    """
    assert permissions.RAT != permissions.TECHRAT
    assert permissions.RAT != permissions.OVERSEER


@pytest.mark.asyncio
@pytest.mark.usefixtures('context_fx')
async def test_restricted_command_inferior(bot_fx, restricted_command_fx):
    context.sender.set('some_recruit')
    context.message.set(f"{Commands.prefix}restricted")
    await context.from_message()
    await Commands.trigger()
    assert not restricted_command_fx.was_called_once


@pytest.mark.asyncio
@pytest.mark.usefixtures('context_fx')
async def test_restricted_command_exact(bot_fx, restricted_command_fx):
    context.sender.set('some_ov')
    context.message.set(f"{Commands.prefix}restricted")
    await context.from_message()
    await Commands.trigger()
    assert restricted_command_fx.was_called_once


@pytest.mark.asyncio
@pytest.mark.usefixtures('context_fx')
async def test_restricted_command_superior(bot_fx, restricted_command_fx):
    context.sender.set('some_admin')
    context.message.set(f"{Commands.prefix}restricted")
    await context.from_message()
    await Commands.trigger()
    assert restricted_command_fx.was_called_once


def test_hash():
    for perm1, perm2 in product(permissions._by_vhost.values(), permissions._by_vhost.values()):
        if perm1 == perm2:
            assert hash(perm1) == hash(perm2)
        else:
            assert hash(perm1) != hash(perm2)


@pytest.mark.asyncio
async def test_require_channel_valid(bot_fx):
    """Verifies @require_channel does not stop commands invoked in a channel"""
    context.channel.set("#unit_test")
    context.target.set(("#unit_test"))

    @require_channel(_message="https://www.youtube.com/watch?v=gvdf5n-zI14")
    async def potato():
        return "hi there!"

    retn = await potato()
    assert retn == "hi there!"


@pytest.mark.asyncio
async def test_require_channel_invalid(bot_fx):
    """verifies require_channel stops commands invoked in PM contexts"""
    context.target.set(bot_fx.nickname)
    context.bot.set(bot_fx)
    context.channel.set(None)

    @require_channel
    async def potato():
        await context.reply("hi there!")

    await potato()

    assert bot_fx.sent_messages[0]['message'] == "This command must be invoked in a channel."


@pytest.mark.asyncio
async def test_require_channel_bare_channel(bot_fx):
    """
    Verifies @require_channel behaves properly as a plain invocation behaves as expected
        in a channel context (not called with arguments)
    """
    context.target.set("#unit_test")
    context.bot.set(bot_fx)
    context.channel.set("#unit_test")

    @require_channel
    async def protected():
        """protected function"""
        return "hot potato!"

    data = await protected()
    assert data == "hot potato!"


@pytest.mark.tryfirst
@pytest.mark.asyncio
async def test_require_channel_bare_pm(bot_fx):
    """
    Verifies @require_channel behaves properly as a plain invocation behaves as expected
        in a pm context
    """
    context.target.set(bot_fx.nickname)
    context.channel.set(None)
    context.bot.set(bot_fx)

    @require_channel
    async def protected():
        """protected function"""
        return "hot potato!"

    retn = await protected()
    assert retn is None
    assert "This command must be invoked in a channel." == bot_fx.sent_messages[0]['message']


@pytest.mark.parametrize("message", ["nope.", "https://www.youtube.com/watch?v=gvdf5n-zI14"])
@pytest.mark.asyncio
async def test_require_channel_call_channel(message: str):
    """
    Verifies @require_channel behaves properly as a plain invocation behaves as expected
        in a channel context
    """
    context.target.set("#unit_test")
    context.channel.set("#unit_test")

    @require_channel(_message=message)
    async def protected():
        """protected function"""
        return "hot potato!"

    data = await protected()
    assert data == "hot potato!"


@pytest.mark.parametrize("message", ["nope.", "https://www.youtube.com/watch?v=gvdf5n-zI14"])
@pytest.mark.asyncio
async def test_require_channel_call_pm(bot_fx, message: str):
    """
    Verifies @require_channel behaves properly as a plain invocation behaves as expected
        in a pm context
    """
    context.target.set("some_rando")
    context.channel.set(None)
    context.bot.set(bot_fx)

    @require_channel(_message=message)
    async def protected():
        """protected function"""
        return "hot potato!"

    data = await protected()
    assert data is None
    assert message == bot_fx.sent_messages[0]['message']


@pytest.mark.asyncio
async def test_require_dm_valid(bot_fx):
    context.message.set("diiirect message!")
    context.target.set(bot_fx.nickname)
    context.channel.set(None)

    @require_dm()
    async def potato():
        return "hi there!"

    retn = await potato()
    assert retn == "hi there!"


@pytest.mark.asyncio
async def test_require_dm_invalid():
    context.channel.set("#unit_test")
    context.target.set("#unit_test")

    @require_dm()
    async def potato():
        return "oh noes!"

    retn = await potato()
    assert retn != "oh noes!"


@pytest.mark.parametrize("vhost",
                         [{"unittest.fuelrats.com"}, {"potato.fuelrats.com"}, {"i.see.all"}])
def test_permission_registers_vhost(vhost, monkeypatch):
    """Verifies a created Permission registers its vhosts"""

    # ensure _by_vhost is clean prior to running test
    monkeypatch.setattr("Modules.permissions._by_vhost", {})

    permission = Permission(1, vhost)
    assert vhost == (set(permissions._by_vhost.keys()))


@pytest.mark.parametrize("vhost_alpha", [{"techrat.fuelrats.com", "op.fuelrats.com"},
                                         {"cannonfodder.fuelrats.com"}])
@pytest.mark.parametrize("vhost_beta", [
    {"i.see.all"},
    {"rats.fuelrats.com", "dispatch.fuelrats.com"}
])
def test_permission_change_vhosts(
        monkeypatch,
        vhost_alpha: Set[str],
        vhost_beta: Set[str]):
    """Verifies the functionality of changing a Permission's vhosts property"""
    # ensure _by_vhost is clean prior to running test
    monkeypatch.setattr("Modules.permissions._by_vhost", {})

    alpha = Permission(1, {"snafu.com"})
    beta = Permission(2, {"FUBAR.com"})

    alpha.vhosts = vhost_alpha
    beta.vhosts = vhost_beta
    # assert the new keys got into the _by_vhost dict

    for vhost in vhost_alpha:
        assert vhost in permissions._by_vhost

    for vhost in vhost_beta:
        assert vhost in permissions._by_vhost

    assert "snafu.com" not in permissions._by_vhost.keys()
    assert "FUBAR.com" not in permissions._by_vhost.keys()


@pytest.mark.parametrize("garbage", [None, dict(), 42, -1])
def test_permission_vhost_setter_garbage(garbage):
    with pytest.raises(TypeError):
        permissions.TECHRAT.vhosts = garbage


def test_permission_denied_message(monkeypatch):
    # ensure _by_vhost is clean prior to running test
    monkeypatch.setattr("Modules.permissions._by_vhost", {})
    permission = Permission(0, {"test.fuelrats.com"}, "heck no.")
    assert permission.denied_message == "heck no."

    permission.denied_message = "nope.avi"
    assert permission.denied_message == "nope.avi"


@pytest.mark.parametrize("garbage", [None, dict(), 42, -1])
def test_denied_message_garbage(garbage, permission_fx: Permission):
    # ensure _by_vhost is clean prior to running test

    with pytest.raises(TypeError):
        permission_fx.denied_message = garbage
