"""
test_rat_command.py

Tests for the rat_command module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import unittest
from unittest import mock

import asyncio
import pydle
from aiounittest import async_test

from Modules.rat_command import Commands, CommandNotFoundException, NameCollisionException,\
    CommandException
from tests.mock_bot import MockBot


class RatCommandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # set the bot to something silly, at least its not None.
        # (this won't cut it for proper commands but works here.)
        # as we are not creating commands that do stuff with bot. duh.
        # these are tests after all.
        Commands.bot = MockBot()
        super().setUpClass()

    def setUp(self):
        # this way command registration between individual tests don't
        # interfere and cause false positives/negatives.
        Commands._flush()
        super().setUp()

    @async_test
    async def test_command_decorator_single(self):
        """
        Verify`Commands.command` decorator can handle string registrations
        """
        # bunch of commands to test
        alias = ['potato', 'cannon', 'Fodder', "fireball"]

        for command in alias:
            with self.subTest(command=command):
                @Commands.command(command)
                async def potato(bot: pydle.Client, channel: str, sender: str):
                    # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
                    return bot, channel, sender

            assert command in Commands._registered_commands.keys()

    def test_command_decorator_list(self):
        aliases = ['potato', 'cannon', 'Fodder', 'fireball']

        # register the command
        @Commands.command(*aliases)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            return bot, channel, sender

        for name in aliases:
            with self.subTest(name=name):
                assert name in Commands._registered_commands.keys()

    @async_test
    async def test_invalid_command(self):
        """
        Ensures the proper exception is raised when a command is not found.
        :return:
        """
        with self.assertRaises(CommandNotFoundException):
            await Commands.trigger(message="!nope", sender="unit_test",
                                   channel="foo")

    def test_double_command_registration(self):
        """
        test verifying it is not possible to register a command twice.
        this prevents oddities where commands are bound but the bind is
        overwritten....
        """
        alias = ['potato', 'cannon', 'Fodder', 'fireball']
        # TODO: move these common lists to setup_class
        # lets define them initially.
        for name in alias:
            @Commands.command(name)
            async def foo():
                pass

            with self.subTest(name=name):
                with self.assertRaises(NameCollisionException):
                    @Commands.command(name)
                    async def bar():
                        pass

    @async_test
    async def test_call_command(self):
        """
        Verifiy that found commands can be invoked via Commands.Trigger()
        :return:
        """
        aliases = ['potato', 'cannon', 'Fodder', 'fireball']
        trigger_alias = [f"{Commands.prefix}{name}" for name in aliases]
        input_sender = "unit_test[BOT]"
        input_channel = "#unit_testing"

        @Commands.command(*aliases)
        async def potato(bot, trigger):
            # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
            return bot, trigger.channel, trigger.nickname

        for command in trigger_alias:
            with self.subTest(command=command):
                out_bot, out_channel, out_sender = await Commands.trigger(
                    message=command, sender=input_sender,
                    channel=input_channel)
                self.assertEqual(input_sender, out_sender)
                self.assertEqual(input_channel, out_channel)
                self.assertIsNotNone(out_bot)

    @mock.patch("Modules.rat_command.Commands.bot")
    @async_test
    async def test_null_bot(self, mock_bot):
        """
        Verifies the correct exception is raised when someone forgets to set
        Commands.bot <.<
        Overkill?
        :return:
        """
        # this is the default value, which should be overwritten during
        #  MechaClient init...
        with self.assertRaises(CommandException):
            await Commands.trigger(
                message="!message",
                sender="unit_test[BOT]",
                channel="unit_tests")

    def test_register_non_callable(self):
        """
        Verifies the correct exception is raised when someone tries to register
         something that is not callable.
        not sure how they would do this outside of calling the private directly
         or why...
        :return:
        """
        foo = [12, None, "str"]
        for item in foo:
            with self.subTest(item=item):
                self.assertFalse(Commands._register(item, ['foo']))

    @async_test
    async def test_rule(self):
        """Verifies that the rule decorator works as expected."""
        underlying = mock.MagicMock()
        Commands.rule("banan(a|e)")(asyncio.coroutine(underlying))

        with self.subTest("matching"):
            await Commands.trigger("!banana", "unit_test", "#mordor")
            assert underlying.called

        underlying.reset_mock()

        with self.subTest("not matching"):
            with self.assertRaises(CommandNotFoundException):
                await Commands.trigger("!banan", "unit_test", "theOneWithTheHills")
            assert not underlying.called
