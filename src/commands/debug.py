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
from src.packages.permissions.permissions import require_permission, TECHRAT, require_channel
from src.packages.utils import Platforms, Status
from loguru import logger


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
async def cmd_superping(context: Context):
    """
    A debug command to coerce mecha to respond.
    """

    await context.reply("pong!")


@command("getConfigPlugins")
@require_channel
@require_permission(TECHRAT)
async def cmd_get_plugins(context: Context):
    """Lists configuration plugins"""
    await context.reply(f"getting plugins...")

    plugins = PLUGIN_MANAGER.list_name_plugin()
    names = [plugin[0] for plugin in plugins]
    await context.reply(",".join(names))


@command("debug-case")
@require_channel
@require_permission(TECHRAT)
async def cmd_create_debug_case(context: Context):
    debug_rescue = await context.bot.board.create_rescue(client="Shatt", system="HIP 21991",
                                                         platform=Platforms.PC,
                                                         active=True,
                                                         status=Status.OPEN)

    await context.reply(f"Created Debug Case as case #{debug_rescue.board_index}!")
    await context.reply(f"Client: {debug_rescue.client}    System: {debug_rescue.system}")


@command("debug-cr")
@require_channel
@require_permission(TECHRAT)
async def cmd_create_debug_case(context: Context):
    debug_rescue = await context.bot.board.create_rescue(client="ShattCR", system="HIP 21991",
                                                         platform=Platforms.PC,
                                                         active=True,
                                                         status=Status.OPEN,
                                                         code_red=True)

    await context.reply(f"Created Debug Case as case #{debug_rescue.board_index}!")
    await context.reply(f"Client: {debug_rescue.client}    System: {debug_rescue.system}")