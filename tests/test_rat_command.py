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

from Modules.commands import NameCollision
from Modules.context import Context


@pytest.mark.commands
class TestRatCommand(object):
    @pytest.mark.asyncio
    async def test_invalid_command(self, bot_fx):
        """
        Ensures that nothing happens and `trigger` exits quietly when no command can be found.
        """
        await bot_fx.on_message("#unittest", 'some_ov', "!unknowncommandsad hi!")

    @pytest.mark.parametrize("alias", ['potato', 'cannon', 'Fodder', 'fireball'])
    def test_double_command_registration(self, alias, command_registry_fx):
        """
        test verifying it is not possible to register a command twice.
        this prevents oddities where commands are bound but the bind is
        overwritten....
        """

        # lets define them initially.

        @command_registry_fx.register(alias)
        async def foo():
            pass

        # now prove we can't double assign it
        with pytest.raises(NameCollision):
            @command_registry_fx.register(alias)
            async def foo():
                pass

    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['potato', 'cannon', 'Fodder', 'fireball'])
    async def test_call_command(self, alias, bot_fx, command_registry_fx, callable_fx):
        """
        Verifiy that found commands can be invoked directly
        """

        trigger_alias = f"{bot_fx.prefix}{alias}"

        @command_registry_fx.register(alias)
        async def potato(context: Context):
            # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
            callable_fx(context)

        ctx = await Context.from_message(bot_fx, "#unittest", "unit_test", trigger_alias)
        await command_registry_fx[alias.casefold()](ctx)

        assert callable_fx.was_called
        assert callable_fx.was_called_once

    @pytest.mark.parametrize("garbage", [12, None, "str"])
    def test_register_non_callable(self, garbage, command_registry_fx):
        """
        Verifies the correct exception is raised when someone tries to register
         something that is not callable.
        not sure how they would do this outside of calling the private directly
         or why...
        :return:
        """

        with pytest.raises(TypeError):
            command_registry_fx.register(garbage)("garbage")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['potato', 'cannon', 'Fodder', "fireball", 'L33tSkillz'])
    async def test_command_decorator_single(self, alias: str, command_registry_fx):
        """
        Verify`command_registry_fx.register` decorator can handle string registrations
        """

        # bunch of commands to test

        @command_registry_fx.register(alias)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
            return bot, channel, sender

        assert alias.casefold() in command_registry_fx

    @pytest.mark.asyncio
    async def test_command_decorator_list(self, command_registry_fx):
        aliases = ['napalm', 'Ball', 'orange', 'TAngerine']

        # register the command
        @command_registry_fx.register(*aliases)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            return bot, channel, sender

        for name in aliases:
            assert name.casefold() in command_registry_fx

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name", ("unit_test[BOT]", "some_recruit", "some_ov"))
    @pytest.mark.parametrize("trigger_message", ["salad Baton", "Crunchy Cheddar", "POTATOES!",
                                                 "carrots"])
    async def test_command_preserves_arguments(self, trigger_message: str, name: str, bot_fx,
                                               command_registry_fx):
        """
        Verifies commands do not mutate argument words
            - because someone had the bright idea of casting ALL words to lower...
            (that would break things)
        """

        ftrigger = f"!{name} {trigger_message}"
        words = [name] + trigger_message.split(" ")

        @command_registry_fx.register(name)
        async def the_command(context: Context):
            """asserts its arguments equal the outer scope"""
            assert words == context.words

        await bot_fx.on_message("#unittest", name, ftrigger)
