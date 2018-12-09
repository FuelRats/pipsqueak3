"""
test_rat_command.py

Tests for the rat_command module

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import pydle
import pytest

import Modules.rat_command as Commands
from Modules.context import Context
from Modules.rat_command import NameCollisionException


@pytest.fixture
def Setup_fx(bot_fx):
    """Sets up the test environment"""
    Commands._flush()


@pytest.mark.commands
@pytest.mark.usefixtures("Setup_fx")
class TestRatCommand(object):
    @pytest.mark.asyncio
    async def test_invalid_command(self):
        """
        Ensures that nothing happens and `trigger` exits quietly when no command can be found.
        """
        await Commands.trigger(Context(None, None, "#unit_test", ['!unknowncommandsad hi!'],
                                       ['!unknowncommandsad hi!', "hi!"]))

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
    async def test_call_command(self, alias, bot_fx):
        """
        Verifiy that found commands can be invoked via Commands.Trigger()
        """
        Commands._flush()

        trigger_alias = f"{Commands.prefix}{alias}"

        @Commands.command(alias)
        async def potato(context: Context):
            # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
            return context.bot, context.channel, context.user.nickname

        ctx = await Context.from_message(bot_fx, "#unittest", "unit_test", trigger_alias)
        retn = await Commands.trigger(ctx)
        out_bot, out_channel, out_sender = retn

        assert 'unit_test' == out_sender
        assert "#unittest" == out_channel

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
    async def test_command_preserves_arguments(self, trigger_message: str, name: str, bot_fx):
        """
        Verifies commands do not mutate argument words
            - because someone had the bright idea of casting ALL words to lower...
            (that would break things)
        """
        Commands._flush()
        ftrigger = f"!{name} {trigger_message}"
        words = [name] + trigger_message.split(" ")

        @Commands.command(name)
        async def the_command(context: Context):
            """asserts its arguments equal the outer scope"""
            assert words == context.words

        ctx = await Context.from_message(bot_fx, "#unit_test", "unit_test", ftrigger)
        await Commands.trigger(ctx)
