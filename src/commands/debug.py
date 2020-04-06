"""
debug.py - Debug and diagnostics commands

Provides IRC commands geared towards debugging mechasqueak itself.
This module should **NOT** be loaded in a production environment

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from src.config import PLUGIN_MANAGER
from src.packages.commands import command
from src.packages.context.context import Context
from src.packages.permissions.permissions import (
    require_permission,
    TECHRAT,
    require_channel,
)
from src.packages.utils import Platforms, Status

from loguru import logger
import humanfriendly
from datetime import datetime, timezone


@command("debug-whois")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_whois(context):
    """A debug command for running a WHOIS command.

    Returns
        str: string repreentation
    """
    data = await context.bot.whois(context.words[1])
    logger.debug(data)
    await context.reply(f"{data}")


@command("debug-userinfo")
@require_permission(TECHRAT)
@require_channel
async def cmd_debug_userinfo(context: Context):
    """
    A debug command for getting information about a user.
    """

    await context.reply(f"triggering user is {context.user.nickname}, {context.user.hostname}")
    await context.reply(f"user identifed?: {context.user.identified}")


@command("superPing!")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_superping(context: Context):
    """
    A debug command to coerce mecha to respond.
    """

    await context.reply("pong!")


@command("getConfigPlugins")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_get_plugins(context: Context):
    """Lists configuration plugins"""
    await context.reply(f"getting plugins...")

    plugins = PLUGIN_MANAGER.list_name_plugin()
    names = [plugin[0] for plugin in plugins]
    await context.reply(",".join(names))


@command("debug-lastmsg")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_lastmessage(context: Context):
    """Get last message sent by user"""
    specified_user = context.words[1].casefold()
    await context.reply(f"Last message from {specified_user}:")
    await context.reply(f"{context.bot.last_user_message[specified_user]!r}")


@command("debug-case")
@require_channel
@require_permission(TECHRAT)
async def cmd_create_debug_case(context: Context):
    debug_rescue = await context.bot.board.create_rescue(
        client="Shatt", system="HIP 21991", platform=Platforms.PC, active=True, status=Status.OPEN,
    )

    await context.reply(f"Created Debug Case as case #{debug_rescue.board_index}!")
    await context.reply(f"Client: {debug_rescue.client}    System: {debug_rescue.system}")
    await context.reply(f"API ID: {debug_rescue.api_id}")


@command("debug-cr")
@require_channel
@require_permission(TECHRAT)
async def cmd_create_debug_case(context: Context):
    debug_rescue = await context.bot.board.create_rescue(
        client="ShattCR",
        system="HIP 21991",
        platform=Platforms.PC,
        active=True,
        status=Status.OPEN,
        code_red=True,
    )

    await context.reply(f"Created Debug Case as case #{debug_rescue.board_index}!")
    await context.reply(f"Client: {debug_rescue.client}    System: {debug_rescue.system}")


@command("debug-eol")
@require_channel
@require_permission(TECHRAT)
async def cmd_words_eol(context: Context):
    await context.reply(f"EOL: {context.words_eol}")


@command("debug-starttime")
@require_channel
@require_permission(TECHRAT)
async def cmd_uptime(context: Context):
    timestamp = (
        humanfriendly.format_timespan(
            (datetime.now(tz=timezone.utc) - context.bot.start_time), detailed=False, max_units=2,
        )
        + " ago"
    )
    await context.reply(
        f"This instance was connected on "
        f'{context.bot.start_time.strftime("%b %d %H:%M:%S UTC")} ({timestamp})'
    )


@command("cake")
@require_permission(TECHRAT)
async def cmd_cake(context: Context):
    await context.reply("🎂🎂🎂")  # cake


@command("snickers")
@require_permission(TECHRAT)
async def cmd_cake(context: Context):
    await context.reply("🍫")  # snickers


@command("get_fact")
@require_permission(TECHRAT)
async def cmd_debug_get_fact(context: Context):
    if len(context.words_eol) != 3:
        return await context.reply("usage !get_fact <name> <platform>")
    _, name, lang = context.words
    result = await context.bot.fact_manager.exists(name, lang)
    if not result:
        return await context.reply(f"unable to find fact by name {name!r} with lang {lang!r}")

    fact = await context.bot.fact_manager.find(name, lang)
    if fact is None:
        return await context.reply("fact was somehow null here! (this is an error!)")
    return await context.reply(fact.message)
