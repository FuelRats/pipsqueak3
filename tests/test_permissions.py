"""
test_permissions.py

Tests for the permissions module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import unittest

from aiounittest import async_test

from Modules import permissions
from Modules.permissions import require_permission
from Modules.rat_command import Commands
from tests.mock_bot import MockBot


# registration is done in setUp
@require_permission(permissions.OVERSEER)
async def restricted(bot, trigger):
    await trigger.reply("Restricted command was executed.")


class PermissionTests(unittest.TestCase):
    def setUp(self):
        Commands._flush()
        Commands.bot = self.bot = MockBot()
        Commands.command("restricted")(restricted)

    def test_permission_greater(self):
        """
        Tests if Permission_a > Permission_b functions correctly.
        :return:
        """
        self.assertTrue(permissions.RAT > permissions.RECRUIT)
        self.assertTrue(permissions.ADMIN > permissions.RAT)
        self.assertFalse(permissions.RAT > permissions.TECHRAT)

    def test_permission_lesser(self):
        """
        Tests if Permission_a < Permission_b correctly.
        :return:
        """
        self.assertTrue(permissions.RECRUIT < permissions.RAT)
        self.assertTrue(permissions.RAT < permissions.TECHRAT)
        self.assertFalse(permissions.ORANGE < permissions.TECHRAT)

    def test_permission_le(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        self.assertTrue(permissions.ADMIN <= permissions.ADMIN)
        self.assertFalse(permissions.ADMIN <= permissions.RAT)
        self.assertTrue(permissions.ADMIN <= permissions.ORANGE)

    def test_permission_ge(self):
        """
        Tests if Permission_a <= Permission_b correctly.
        :return:
        """
        self.assertTrue(permissions.ADMIN >= permissions.ADMIN)
        self.assertTrue(permissions.ADMIN >= permissions.RAT)
        self.assertFalse(permissions.ADMIN >= permissions.ORANGE)

    def test_permission_equal(self):
        """
        Verifies that Permission_a == Permission_b
        :return:
        """
        self.assertTrue(permissions.RAT == permissions.RAT)
        self.assertTrue(permissions.TECHRAT == permissions.TECHRAT)
        self.assertTrue(permissions.ADMIN == permissions.NETADMIN)

    def test_permission_not_equal(self):
        """
        Verifies that Permission_a != Permission_b
        :return:
        """
        self.assertTrue(permissions.RAT != permissions.TECHRAT)
        self.assertTrue(permissions.DISPATCH != permissions.ORANGE)

    @async_test
    async def test_restricted_command_inferior(self):
        await Commands.trigger("!restricted", "some_recruit", "#somechannel")
        self.assertIn({
            "target": "#somechannel",
            "message": permissions.OVERSEER.denied_message
        }, self.bot.sent_messages)

    @async_test
    async def test_restricted_command_exact(self):
        await Commands.trigger("!restricted", "some_ov", "#somechannel")
        self.assertIn({
            "target": "#somechannel",
            "message": "Restricted command was executed."
        }, self.bot.sent_messages)

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
