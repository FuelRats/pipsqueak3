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
from Modules import permissions
from Modules.context import Context
from Modules.permissions import require_permission, require_channel, require_dm, Permission


@pytest.fixture
def Setup_fx(bot_fx):
    """Sets up the test environment"""
    Commands._flush()
    Commands.bot = bot_fx


@pytest.fixture
def restricted_command_fx(async_callable_fx, Setup_fx):
    restricted = require_permission(permissions.OVERSEER)(async_callable_fx)

    Commands.command("restricted")(restricted)
    return async_callable_fx


@pytest.mark.permissions
@pytest.mark.usefixtures("Setup_fx")
class TestPermissions(object):

    def test_permission_greater(self):
        """
        Tests if Permission_a > Permission_b functions correctly.
        :return:
        """
        assert permissions.RAT > permissions.RECRUIT
        assert permissions.ADMIN > permissions.RAT
        assert not permissions.RAT > permissions.TECHRAT

    def test_permission_lesser(self):
        """
        Tests if Permission_a < Permission_b correctly.
        :return:
        """
        assert permissions.RECRUIT < permissions.RAT
        assert permissions.RAT < permissions.TECHRAT
        assert permissions.OVERSEER < permissions.TECHRAT

    def test_permission_le(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        assert permissions.ADMIN <= permissions.ADMIN
        assert not permissions.ADMIN <= permissions.RAT
        assert permissions.OVERSEER <= permissions.ADMIN
        assert not permissions.ADMIN <= permissions.OVERSEER

    def test_permission_ge(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        assert permissions.ADMIN >= permissions.ADMIN
        assert permissions.ADMIN >= permissions.RAT
        assert not permissions.RAT >= permissions.OVERSEER

    def test_permission_equal(self):
        """
        Verifies that Permission_a == Permission_b
        :return:
        """
        assert permissions.RAT == permissions.RAT
        assert permissions.TECHRAT == permissions.TECHRAT
        assert permissions.ADMIN == permissions.ADMIN

    def test_permission_not_equal(self):
        """
        Verifies that Permission_a != Permission_b
        :return:
        """
        assert permissions.RAT != permissions.TECHRAT
        assert permissions.RAT != permissions.OVERSEER

    @pytest.mark.asyncio
    async def test_restricted_command_inferior(self, bot_fx, restricted_command_fx):
        context = await Context.from_message(bot_fx, "#somechannel", "some_recruit", "!restricted")
        await Commands.trigger(context)
        assert not restricted_command_fx.was_called_once

    @pytest.mark.asyncio
    async def test_restricted_command_exact(self, bot_fx, restricted_command_fx):
        context = await Context.from_message(bot_fx, "#somechannel", "some_ov", "!restricted")
        await Commands.trigger(context)
        assert restricted_command_fx.was_called_once

    @pytest.mark.asyncio
    async def test_restricted_command_superior(self, bot_fx, restricted_command_fx):
        context = await Context.from_message(bot_fx, "#somechannel", "some_ov", "!restricted")
        await Commands.trigger(context)
        assert restricted_command_fx.was_called_once

    def test_hash(self):
        for perm1, perm2 in product(permissions._by_vhost.values(), permissions._by_vhost.values()):
            if perm1 == perm2:
                assert hash(perm1) == hash(perm2)
            else:
                assert hash(perm1) != hash(perm2)

    @pytest.mark.asyncio
    async def test_require_channel_valid(self, bot_fx, context_channel_fx):
        """Verifies @require_channel does not stop commands invoked in a channel"""

        @require_channel(message="https://www.youtube.com/watch?v=gvdf5n-zI14")
        async def potato(context: Context):
            return "hi there!"

        retn = await potato(context_channel_fx)
        assert retn == "hi there!"

    @pytest.mark.asyncio
    async def test_require_channel_invalid(self, context_pm_fx, bot_fx):
        """verifies require_channel stops commands invoked in PM contexts"""

        @require_channel
        async def potato(context: Context):
            context.reply("hi there!")

        await potato(context_pm_fx)

        assert "This command must be invoked in a channel." == bot_fx.sent_messages[0]['message']

    @pytest.mark.asyncio
    async def test_require_channel_bare_channel(self, context_channel_fx: Context):
        """
        Verifies @require_channel behaves properly as a plain invocation behaves as expected
            in a channel context
        """

        @require_channel
        async def protected(context: Context):
            """protected function"""
            return "hot potato!"

        data = await protected(context_channel_fx)
        assert data == "hot potato!"

    @pytest.mark.asyncio
    async def test_require_channel_bare_pm(self, context_pm_fx: Context, bot_fx):
        """
        Verifies @require_channel behaves properly as a plain invocation behaves as expected
            in a pm context
        """

        @require_channel
        async def protected(context: Context):
            """protected function"""
            return "hot potato!"

        await protected(context_pm_fx)
        assert "This command must be invoked in a channel." == bot_fx.sent_messages[0]['message']

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", ["nope.", "https://www.youtube.com/watch?v=gvdf5n-zI14"])
    async def test_require_channel_call_channel(self, context_channel_fx: Context, message: str):
        """
        Verifies @require_channel behaves properly as a plain invocation behaves as expected
            in a channel context
        """

        @require_channel(message=message)
        async def protected(context: Context):
            """protected function"""
            return "hot potato!"

        data = await protected(context_channel_fx)
        assert data == "hot potato!"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", ["nope.", "https://www.youtube.com/watch?v=gvdf5n-zI14"])
    async def test_require_channel_call_pm(self, context_pm_fx: Context, bot_fx, message: str):
        """
        Verifies @require_channel behaves properly as a plain invocation behaves as expected
            in a pm context
        """

        @require_channel(message=message)
        async def protected(context: Context):
            """protected function"""
            return "hot potato!"

        await protected(context_pm_fx)
        assert message == bot_fx.sent_messages[0]['message']

    @pytest.mark.asyncio
    async def test_require_dm_valid(self, context_pm_fx):
        @require_dm()
        async def potato(context: Context):
            return "hi there!"

        retn = await potato(context_pm_fx)
        assert retn == "hi there!"

    @pytest.mark.asyncio
    async def test_require_dm_invalid(self, context_channel_fx):
        @require_dm()
        async def potato(context: Context):
            return "oh noes!"

        retn = await potato(context_channel_fx)
        assert retn != "oh noes!"

    @pytest.mark.parametrize("vhost",
                             [{"unittest.fuelrats.com"}, {"potato.fuelrats.com"}, {"i.see.all"}])
    def test_permission_registers_vhost(self, vhost, monkeypatch):
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
    def test_permission_change_vhosts(self,
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
    def test_permission_vhost_setter_garbage(self, garbage):
        with pytest.raises(TypeError):
            permissions.TECHRAT.vhosts = garbage

    def test_permission_denied_message(self, monkeypatch):
        # ensure _by_vhost is clean prior to running test
        monkeypatch.setattr("Modules.permissions._by_vhost", {})
        permission = Permission(0, {"test.fuelrats.com"}, "heck no.")
        assert permission.denied_message == "heck no."

        permission.denied_message = "nope.avi"
        assert permission.denied_message == "nope.avi"

    @pytest.mark.parametrize("garbage", [None, dict(), 42, -1])
    def test_denied_message_garbage(self, garbage, permission_fx: Permission):
        # ensure _by_vhost is clean prior to running test

        with pytest.raises(TypeError):
            permission_fx.denied_message = garbage
