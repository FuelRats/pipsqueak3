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

import pydle
from aiounittest import async_test

from Modules.rat_command import Commands, CommandNotFoundException, NameCollisionException, InvalidCommandException, \
    CommandException


class MockBot(object):
    users = {
        "unit_test[BOT]": {
            "nickname": "unit_test[BOT]",
            "username": "unit_test",
            "hostname": "i.see.none",
            "away": False,
            "away_message": None,
            "account": None,
            "identified": True
        },
        "unit_test": {
            "nickname": "unit_test",
            "username": "unit_test",
            "hostname": "i.see.none",
            "away": False,
            "away_message": None,
            "account": None,
            "identified": True
        }
    }

    @classmethod
    def is_channel(cls, channel: str):
        return channel[0] in ("#", "&")


class RatCommandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # set the bot to something silly, at least its not None. (this won't cut it for proper commands but works here.)
        # as we are not creating commands that do stuff with bot. duh. these are tests after all.
        Commands.bot = MockBot()
        super().setUpClass()

    def setUp(self):
        # this way command registration between individual tests don't interfere and cause false positives/negatives.
        Commands._flush()
        super().setUp()

    def test_get_unknown_command(self):
        """
        Verifies that Commands.get_command() returns None if a command is not found
        :return:
        """
        unknown_names = ["foo", "bar", "meatbag", "limpet"]

        @Commands.command("fuel")
        async def potato(*args):
            return True

        for name in unknown_names:
            with self.subTest(name=name):
                self.assertIsNone(Commands.get_command(name))
        with self.subTest(name="fuel"):
            self.assertIsNotNone(Commands.get_command("fuel"))

    @async_test
    async def test_command_decorator_single(self):
        """
        Tests if the `Commands.command` decorator can handle string registrations
        """
        # bunch of commands to test
        alias = ['potato', 'cannon', 'Fodder', "fireball"]
        commands = [f"{Commands.prefix}{name}" for name in alias]

        for command in commands:
            with self.subTest(command=command):
                @Commands.command(command.strip(Commands.prefix))
                async def potato(bot: pydle.Client, channel: str, sender: str):
                    # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
                    return bot, channel, sender
            self.assertIsNotNone(Commands.get_command(command.strip(Commands.prefix)))

    def test_command_decorator_list(self):
        aliases = ['potato', 'cannon', 'Fodder', 'fireball']
        trigger_alias = [f"{Commands.prefix}{name}" for name in aliases]

        # register the command
        @Commands.command(*aliases)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            return bot, channel, sender

        for name in trigger_alias:
            with self.subTest(name=name):
                self.assertIsNotNone(Commands.get_command(name))

    @async_test
    async def test_invalid_command(self):
        """
        Ensures the proper exception is raised when a command is not found.
        :return:
        """
        with self.assertRaises(CommandNotFoundException):
            await Commands.trigger(message="!nope", sender="unit_test", channel="foo")

    def test_double_command_registration(self):
        """
        test verifying it is not possible to register a command twice.
        this prevents odities where commands are bound but the bind is overwritten....
        which leaves the original bound command not called during a trigger event.
        :return:
        """
        alias = ['potato', 'cannon', 'Fodder', 'fireball']  # TODO: move these common lists to setup_class
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
                out_bot, out_channel, out_sender = await Commands.trigger(message=command, sender=input_sender,
                                                                          channel=input_channel)
                self.assertEqual(input_sender, out_sender)
                self.assertEqual(input_channel, out_channel)
                self.assertIsNotNone(out_bot)

    @async_test
    async def test_ignored_message(self):
        """
        Tests if Commands.trigger correctly ignores messages not containing the prefix.
        :return:
        """
        words = ['potato', 'cannon', 'Fodder', 'fireball', "what is going on here!", ".!potato"]
        for word in words:
            with self.subTest(word=word):
                self.assertIsNone(await Commands.trigger(message=word, sender="unit_test[BOT]", channel="unit_tests"))

    @async_test
    async def test_null_message(self):
        """
        Verifies the correct exception is raised when a null message is sent
        :return:
        """
        words = ["", None, '']
        for word in words:
            with self.subTest(word=word):
                with self.assertRaises(InvalidCommandException):
                    await Commands.trigger(message=word, sender="unit_test[BOT]", channel="unit_tests")

    @mock.patch("Modules.rat_command.Commands.bot")
    @async_test
    async def test_null_bot(self, mock_bot):
        """
        Verifies the correct exception is raised when someone forgets to set Commands.bot <.<
        Overkill?
        :return:
        """
        # this is the default value, which should be overwritten during MechaClient init...
        with self.assertRaises(CommandException):
            await Commands.trigger(message="!message", sender="unit_test[BOT]", channel="unit_tests")

    def test_register_non_callable(self):
        """
        Verifies the correct exception is raised when someone tries to register something that is not callable.
        not sure how they would do this outside of calling the private directly or why...
        :return:
        """
        foo = [12, None, "str"]
        for item in foo:
            with self.subTest(item=item):
                self.assertFalse(Commands._register(item, ['foo']))
