"""
debug.py - Debug and diagnostics commands

Provides IRC commands geared towards debugging mechasqueak itself.
This module should **NOT** be loaded in a production environment

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging

from src.config import plugin_manager
from src.packages.commands import command
from src.packages.context.context import Context
from src.packages.permissions.permissions import require_permission, TECHRAT, require_channel

LOG = logging.getLogger(f"mecha.{__name__}")


@command("debug-whois")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_whois(context):
    """A debug command for running a WHOIS command.

    Returns
        str: string repreentation
    """
    data = await context.bot.whois(context.words[1])
    LOG.debug(data)
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


@command("getPlugins")
@require_channel
@require_permission(TECHRAT)
async def cmd_get_plugins(context: Context):
    await context.reply(f"getting plugins...")

    plugins = plugin_manager.list_name_plugin()
    names = [plugin[0] for plugin in plugins]
    await context.reply(",".join(names))


@command("rehash")
@require_channel(message="please do this where everyone can see 😒")
@require_permission(TECHRAT, override_message="no.")
async def cmd_rehash(context: Context):
    """ rehash the hash browns. (reloads config file)"""
    LOG.warning(f"config rehashing invoked by user {context.user.nickname}")
    if not all(plugin_manager.hook.validate_config(data=None)):
        await context.reply(f"config file failed to validate.")
        return

    LOG.info(f"config file validated. applying...")
    plugin_manager.hook.rehash_handler(data=None)
    LOG.info("done applying config file.")
    await context.reply("done rehashing.")
