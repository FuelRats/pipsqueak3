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

import src.packages.commands.rat_command as Commands
from src.packages.commands.rat_command import NameCollisionException
from src.packages.context.context import Context

from loguru import logger


@pytest.mark.unit
@pytest.mark.commands
class TestRatCommand(object):
    @pytest.mark.asyncio
    async def test_invalid_command(self, bot_fx):
        """
        Ensures that nothing happens and `trigger` exits quietly when no command can be found.
        """
        ctx = await Context.from_message(
            bot_fx, "#unittest", "some_recruit", "!unknowncommandsad hi!"
        )
        await Commands.trigger(ctx)

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

        del Commands._registered_commands[alias.casefold()]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['potato', 'cannon', 'Fodder', 'fireball'])
    async def test_call_command(self, alias, bot_fx, configuration_fx):
        """
        Verifiy that found commands can be invoked via Commands.Trigger()
        """

        trigger_alias = f"{configuration_fx.commands.prefix}{alias}"

        @Commands.command(alias)
        async def potato(context: Context):
            # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
            return context.bot, context.channel, context.user.nickname

        ctx = await Context.from_message(bot_fx, "#unittest", "unit_test", trigger_alias)
        retn = await Commands.trigger(ctx)
        out_bot, out_channel, out_sender = retn

        assert 'unit_test' == out_sender
        assert "#unittest" == out_channel

        del Commands._registered_commands[alias.casefold()]

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

        # bunch of commands to test

        @Commands.command(alias)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            # print(f"bot={bot}\tchannel={channel}\tsender={sender}")
            return bot, channel, sender

        assert alias.lower() in Commands._registered_commands.keys()

        del Commands._registered_commands[alias.casefold()]

    @pytest.mark.asyncio
    async def test_command_decorator_list(self):
        aliases = ['napalm', 'Ball', 'orange', 'TAngerine']

        # register the command
        @Commands.command(*aliases)
        async def potato(bot: pydle.Client, channel: str, sender: str):
            return bot, channel, sender

        for name in aliases:
            assert name.lower() in Commands._registered_commands.keys()

        for name in aliases:
            del Commands._registered_commands[name.casefold()]

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
        if name in Commands._registered_commands:
            del Commands._registered_commands[name.casefold()]
        ftrigger = f"!{name} {trigger_message}"
        words = [name] + trigger_message.split(" ")

        @Commands.command(name)
        async def the_command(context: Context):
            """asserts its arguments equal the outer scope"""
            assert words == context.words

        ctx = await Context.from_message(bot_fx, "#unit_test", "unit_test", ftrigger)
        await Commands.trigger(ctx)

        del Commands._registered_commands[name.casefold()]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['quiet'])
    async def test_call_command_quiet(self, alias, bot_fx, rat_board_fx, configuration_fx, random_string_fx):
        """
        Verifiy that the !quiet command returns useful information
        """
        trigger_alias = f"{configuration_fx.commands.prefix}{alias}"
        logger.debug(f"Triggering alias: {trigger_alias}")
        bot_fx.board = rat_board_fx
        ctx = await Context.from_message(bot_fx, "#unittest", "some_rat", trigger_alias)

        # Pre-case creation
        retn = await Commands.trigger(ctx)
        logger.debug(f"sent pre: {bot_fx.sent_messages} - lastcase: {rat_board_fx.last_case_datetime}")
        assert "Got no information yet" in bot_fx.sent_messages[0]['message']

        # During case active
        rescue = await rat_board_fx.create_rescue(client=random_string_fx)
        retn = await Commands.trigger(ctx)
        logger.debug(f"sent active: {bot_fx.sent_messages} - lastcase: {rat_board_fx.last_case_datetime}")
        assert "There is corrently an active rescue" in bot_fx.sent_messages[1]['message']

        # Post-case active
        await rat_board_fx.remove_rescue(rescue._board_index)
        retn = await Commands.trigger(ctx)
        logger.debug(f"sent post: {bot_fx.sent_messages} - lastcase: {rat_board_fx.last_case_datetime}")
        assert "The last case was created 0 minutes ago." in bot_fx.sent_messages[2]['message']


    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['active', 'inactive', 'activate', 'deactivate'])
    async def test_call_command_active_no_inject(self, alias, bot_fx, rat_board_fx, configuration_fx, random_string_fx):
        """
        Verifiy that the !active command toggles the case active state when no injection message is passed
        At the same time, verify the bot output
        """
        rescue = await rat_board_fx.create_rescue(client=random_string_fx)
        trigger_alias = f"{configuration_fx.commands.prefix}{alias} {rescue.board_index}"
        logger.debug(f"Triggering alias: {trigger_alias}")
        bot_fx.board = rat_board_fx
        ctx = await Context.from_message(bot_fx, "#unittest", "some_rat", trigger_alias)

        # Pre-case creation
        default_state = rat_board_fx.get(rescue.board_index).active
        logger.debug(f"Default active state: {default_state}")
        assert default_state

        # De-activate case
        retn = await Commands.trigger(ctx)
        toggled_state = rat_board_fx.get(rescue.board_index).active
        logger.debug(f"Toggled active state (1): {toggled_state}")
        assert not toggled_state

        # Re-activate case
        retn = await Commands.trigger(ctx)
        toggled_state = rat_board_fx.get(rescue.board_index).active
        logger.debug(f"Toggled active state (2): {toggled_state}")
        assert toggled_state

        # Check bot output
        logger.debug(f"Messages sent: {bot_fx.sent_messages}")
        assert f"{random_string_fx}'s case is now Inactive." in bot_fx.sent_messages[0]['message']
        assert f"{random_string_fx}'s case is now Active." in bot_fx.sent_messages[1]['message']


    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['active', 'inactive', 'activate', 'deactivate'])
    async def test_call_command_active_with_inject(self, alias, bot_fx, rat_board_fx, configuration_fx, random_string_fx):
        """
        Verifiy that the !active command toggles the case active state when an injection message is passed
        At the same time, verify the bot output
        """
        rescue = await rat_board_fx.create_rescue(client=random_string_fx)
        trigger_alias = f"{configuration_fx.commands.prefix}{alias} {rescue.board_index} test inject message"
        logger.debug(f"Triggering alias: {trigger_alias}")
        bot_fx.board = rat_board_fx
        ctx = await Context.from_message(bot_fx, "#unittest", "some_rat", trigger_alias)

        # Pre-case creation
        default_state = rat_board_fx.get(rescue.board_index).active
        logger.debug(f"Default active state: {default_state}")
        assert default_state

        # De-activate case
        retn = await Commands.trigger(ctx)
        toggled_state = rat_board_fx.get(rescue.board_index).active
        logger.debug(f"Toggled active state (1): {toggled_state}")
        assert not toggled_state

        # Re-activate case
        retn = await Commands.trigger(ctx)
        toggled_state = rat_board_fx.get(rescue.board_index).active
        logger.debug(f"Toggled active state (2): {toggled_state}")
        assert toggled_state

        # Check bot output
        logger.debug(f"Messages sent: {bot_fx.sent_messages}")
        assert f"{random_string_fx}'s case updated with: 'test inject message' (Case {rescue.board_index})" in bot_fx.sent_messages[0]['message']
        assert f"{random_string_fx}'s case is now Inactive." in bot_fx.sent_messages[1]['message']
        assert f"{random_string_fx}'s case updated with: 'test inject message' (Case {rescue.board_index})" in bot_fx.sent_messages[2]['message']
        assert f"{random_string_fx}'s case is now Active." in bot_fx.sent_messages[3]['message']


    @pytest.mark.asyncio
    @pytest.mark.parametrize("alias", ['md', 'mdadd'])
    @pytest.mark.parametrize("channel", ['#unittest', 'some_rat'])
    async def test_call_command_md(self, alias, channel, bot_fx, configuration_fx, rat_board_fx, rescue_sop_fx):
        assert rescue_sop_fx.marked_for_deletion.marked == False, "UNEXPECTED: SOP rescue already marked for deletion"
        bot_fx.board = rat_board_fx
        await bot_fx.board.append(rescue_sop_fx)
        assert len(bot_fx.board) == 1, f"Setting up a test case failed"

        trigger_alias = f"{configuration_fx.commands.prefix}{alias} {rescue_sop_fx.board_index}"
        logger.debug(f"Triggering alias: {trigger_alias}")
        await Commands.trigger(await Context.from_message(bot_fx, channel, "some_rat", trigger_alias))
        assert len(bot_fx.board) == 1, f"Case got closed by {trigger_alias} [without inject message]"
        assert not rescue_sop_fx.marked_for_deletion.marked, "SOP rescue became marked for deletion [without inject message]"

        trigger_alias = f"{configuration_fx.commands.prefix}{alias} {rescue_sop_fx.board_index} Closing test case"
        logger.debug(f"Triggering alias: {trigger_alias}")
        await Commands.trigger(await Context.from_message(bot_fx, channel, "some_rat", trigger_alias))
        assert len(bot_fx.board) == 0, f"Case did not get closed by {trigger_alias}"
        assert rescue_sop_fx.marked_for_deletion.marked, "SOP rescue did not become marked for deletion"
