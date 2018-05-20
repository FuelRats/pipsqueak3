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
from aiounittest import async_test

from Modules import permissions
from Modules.permissions import require_permission
from Modules.rat_command import Commands
from Modules.user import User
from tests.mock_bot import MockBot


# registration is done in setUp
@require_permission(permissions.OVERSEER)
async def restricted(bot, trigger):
    await trigger.reply("Restricted command was executed.")


class TestPermission(object):
    def setup_module(self):
        Commands._flush()
        Commands.bot = self.bot = MockBot()
        Commands.command("restricted")(restricted)

    def test_permission_greater(self):
        """
        Tests if Permission_a > Permission_b functions correctly.
        :return:
        """
        assert (permissions.RAT > permissions.RECRUIT)
        assert (permissions.ADMIN > permissions.RAT)
        assert not (permissions.RAT > permissions.TECHRAT)

    def test_permission_lesser(self):
        """
        Tests if Permission_a < Permission_b correctly.
        :return:
        """
        assert (permissions.RECRUIT < permissions.RAT)
        assert (permissions.RAT < permissions.TECHRAT)
        assert not (permissions.ORANGE < permissions.TECHRAT)

    def test_permission_le(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        assert (permissions.ADMIN <= permissions.ADMIN)
        assert not (permissions.ADMIN <= permissions.RAT)
        assert (permissions.ADMIN <= permissions.ORANGE)

    def test_permission_ge(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        assert (permissions.ADMIN >= permissions.ADMIN)
        assert (permissions.ADMIN >= permissions.RAT)
        assert not (permissions.ADMIN >= permissions.ORANGE)

    def test_permission_equal(self):
        """
        Verifies that Permission_a == Permission_b
        :return:
        """
        assert (permissions.RAT == permissions.RAT)
        assert (permissions.TECHRAT == permissions.TECHRAT)
        assert (permissions.ADMIN == permissions.NETADMIN)

    def test_permission_not_equal(self):
        """
        Verifies that Permission_a != Permission_b
        :return:
        """
        assert (permissions.RAT != permissions.TECHRAT)
        assert (permissions.DISPATCH != permissions.ORANGE)

    @async_test
    async def test_restricted_command_inferior(self):
        user = User("some_recruit", "recruit.fuelrats.com", "some_recruit", "some_recruit", False,
                    "some_recruit", identified=True)
        await Commands.trigger("!restricted", await User.from_bot(self.bot, "some_recruit"),
                               "#somechannel")
        assert {
                   "target": "#somechannel",
                   "message": permissions.OVERSEER.denied_message
               } in self.bot.sent_messages

    @pytest.mark.asyncio
    async def test_restricted_command_exact(self, bot_fx):
        await Commands.trigger("!restricted", await User.from_bot(bot_fx, "some_ov"),
                               "#somechannel")
        assert {
                   "target": "#somechannel",
                   "message": "Restricted command was executed."
               } in bot_fx.sent_messages

    @async_test
    async def test_restricted_command_superior(self):
        await Commands.trigger("!restricted", "some_admin", "#somechannel")
        self.assertIn({
            "target": "#somechannel",
            "message": "Restricted command was executed."
        }, self.bot.sent_messages)

    @async_test
    async def test_restricted_command_not_identified(self):
        await Commands.trigger("!restricted", "authorized_but_not_identified",
                               "#somechannel")
        self.assertIn({
            "target": "#somechannel",
            "message": permissions.OVERSEER.denied_message
        }, self.bot.sent_messages)

    def test_hash(self):
        for perm1, perm2 in product(permissions._by_vhost.values(), permissions._by_vhost.values()):
            if perm1 == perm2:
                assert hash(perm1) == hash(perm2)
            else:
                assert hash(perm1) != hash(perm2)
