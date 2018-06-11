"""
test_permissions.py

Tests for the permissions module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from itertools import product

import pytest

from Modules import permissions
from Modules.permissions import require_permission
from Modules.rat_command import Commands


# registration is done in setUp
@require_permission(permissions.OVERSEER)
async def restricted(context):
    await context.reply("Restricted command was executed.")


@pytest.fixture
def Setup_fx(bot_fx):
    """Sets up the test environment"""
    Commands._flush()
    Commands.bot = bot_fx
    Commands.command("restricted")(restricted)


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
        assert not permissions.ORANGE < permissions.TECHRAT

    def test_permission_le(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        assert permissions.ADMIN <= permissions.ADMIN
        assert not permissions.ADMIN <= permissions.RAT
        assert permissions.ADMIN <= permissions.ORANGE

    def test_permission_ge(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        assert permissions.ADMIN >= permissions.ADMIN
        assert permissions.ADMIN >= permissions.RAT
        assert not permissions.ADMIN >= permissions.ORANGE

    def test_permission_equal(self):
        """
        Verifies that Permission_a == Permission_b
        :return:
        """
        assert permissions.RAT == permissions.RAT
        assert permissions.TECHRAT == permissions.TECHRAT
        assert permissions.ADMIN == permissions.NETADMIN

    def test_permission_not_equal(self):
        """
        Verifies that Permission_a != Permission_b
        :return:
        """
        assert permissions.RAT != permissions.TECHRAT
        assert permissions.DISPATCH != permissions.ORANGE

    @pytest.mark.asyncio
    async def test_restricted_command_inferior(self, bot_fx):
        await Commands.trigger("!restricted", "some_recruit", "#somechannel")
        assert {
                   "target": "#somechannel",
                   "message": permissions.OVERSEER.denied_message
               } in bot_fx.sent_messages

    @pytest.mark.asyncio
    async def test_restricted_command_exact(self, bot_fx):
        await Commands.trigger("!restricted", "some_ov", "#somechannel")
        assert {
                   "target": "#somechannel",
                   "message": "Restricted command was executed."
               } in bot_fx.sent_messages

    @pytest.mark.asyncio
    async def test_restricted_command_superior(self, bot_fx):
        await Commands.trigger("!restricted", "some_admin", "#somechannel")
        assert {
                   "target": "#somechannel",
                   "message": "Restricted command was executed."
               } in bot_fx.sent_messages

    @pytest.mark.asyncio
    async def test_restricted_command_not_identified(self, bot_fx):
        await Commands.trigger("!restricted", "authorized_but_not_identified",
                               "#somechannel")
        assert {
                   "target": "#somechannel",
                   "message": permissions.OVERSEER.denied_message
               } in bot_fx.sent_messages

    def test_hash(self):
        for perm1, perm2 in product(permissions._by_vhost.values(), permissions._by_vhost.values()):
            if perm1 == perm2:
                assert hash(perm1) == hash(perm2)
            else:
                assert hash(perm1) != hash(perm2)
