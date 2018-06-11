"""
test_rat_command.py

Tests for the rat_command module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import asyncio
from unittest import mock

import pydle
import pytest

import Modules.rat_command as Commands
from Modules.context import Context
from Modules.rat_command import CommandNotFoundException, NameCollisionException


@pytest.fixture
def Setup_fx(bot_fx):
    """Sets up the test environment"""
    Commands._flush()
    Commands.bot = bot_fx


@pytest.mark.usefixtures("Setup_fx")
class TestRatCommand(object):

    @pytest.mark.asyncio
    async def test_invalid_command(self):
        """
        Ensures the proper exception is raised when a command is not found.
        :return:
        """
        with pytest.raises(CommandNotFoundException):
            await Commands.trigger(message="!nope", sender="unit_test",
                                   channel="foo")

    @pytest.mark.parametrize("alias", ['potato', 'cannon', 'Fodder', 'fireball'])
    def test_double_command_registration(self, alias):
        """
        test verifying it is not possible to register a command twice.
        this prevents oddities where commands are bound but the bind is
        overwritten....
        """

        # lets define them initially.

        @Commands.command(alias)
        async def foo():
            pass

        # now prove we can't double assign it
        with pytest.raises(NameCollisionException):
            @Commands.command(alias)
            async def foo():
                pass

    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['potato', 'cannon', 'Fodder', 'fireball'])
    async def test_call_command(self, alias):
        """
        Verifiy that found commands can be invoked via Commands.Trigger()
        """
        Commands._flush()

        trigger_alias = f"{Commands.prefix}{alias}"
        input_sender = "unit_test[BOT]"
        input_channel = "#unit_testing"

        @Commands.command(alias)
        async def potato(context: Context):
            # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
            return context.bot, context.channel, context.user.nickname

        out_bot, out_channel, out_sender = await Commands.trigger(
            message=trigger_alias, sender=input_sender,
            channel=input_channel)
        assert input_sender == out_sender
        assert input_channel == out_channel

    @pytest.mark.parametrize("garbage", [12, None, "str"])
    def test_register_non_callable(self, garbage):
        """
        Verifies the correct exception is raised when someone tries to register
         something that is not callable.
        not sure how they would do this outside of calling the private directly
         or why...
        :return:
        """
        assert Commands._register(garbage, ['foo']) is False

    @pytest.mark.asyncio
    async def test_rule_matching(self):
        """Verifies that the rule decorator works as expected."""
        underlying = mock.MagicMock()
        Commands.rule("banan(a|e)")(asyncio.coroutine(underlying))

        await Commands.trigger("!banana", "unit_test", "#mordor")
        assert underlying.called

        underlying.reset_mock()

    @pytest.mark.asyncio
    async def test_rule_not_matching(self):
        """verifies that the rule decorator works as expected."""
        underlying = mock.MagicMock()
        Commands.rule("banan(a|e)")(asyncio.coroutine(underlying))
        with pytest.raises(CommandNotFoundException):
            await Commands.trigger("!banan", "unit_test", "theOneWithTheHills")
        assert not underlying.called

    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['potato', 'cannon', 'Fodder', "fireball"])
    async def test_command_decorator_single(self, alias: str):
        """
        Verify`Commands.command` decorator can handle string registrations
        """
        Commands._flush()

        # bunch of commands to test

        @Commands.command(alias)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
            return bot, channel, sender

        assert alias.lower() in Commands._registered_commands.keys()

    @pytest.mark.asyncio
    async def test_command_decorator_list(self):
        aliases = ['napalm', 'Ball', 'orange', 'TAngerine']

        # register the command
        @Commands.command(*aliases)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            return bot, channel, sender

        for name in aliases:
            assert name.lower() in Commands._registered_commands.keys()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name", ("unit_test[BOT]", "some_recruit", "some_ov"))
    @pytest.mark.parametrize("trigger_message", ["salad Baton", "Crunchy Cheddar", "POTATOES!",
                                                 "carrots"])
    async def test_command_preserves_arguments(self, trigger_message: str, name: str):
        """
        Verifies commands do not mutate argument words
            - because someone had the bright idea of casting ALL words to lower...
            (that would break things)
        """
        Commands._flush()
        ftrigger = f"!{name} {trigger_message}"
        words = [name.lower()] + trigger_message.split(" ")

        @Commands.command(name)
        async def the_command(context: Context):
            """asserts its arguments equal the outer scope"""
            assert context.words == words

        await Commands.trigger(ftrigger, "unit_test[BOT]", "#unit_tests")
