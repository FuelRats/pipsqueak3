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

from Modules.context import Context
from Modules.permissions import require_permission, TECHRAT, RAT, require_channel
from Modules.rat_command import command

log = logging.getLogger(f"mecha.{__name__}")


@require_permission(RAT)
@command("ping")
async def cmd_ping(context: Context):
    """
    Pongs a ping. lets see if the bots alive (command decorator testing)
    :param context: `Context` object for the command call.
    """
    log.warning(f"cmd_ping triggered on channel '{context.channel}' for user "
                f"'{context.user.nickname}'")
    await context.reply(f"{context.user.nickname} pong!")


@command("debug-whois")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_whois(context):
    """A debug command for running a WHOIS command.

    Returns
        str: string repreentation
    """
    data = await context.bot.whois(context.words[1])
    log.debug(data)
    await context.reply(f"{data}")


@command("debug-userinfo")
@require_permission(TECHRAT)
@require_channel
async def cmd_debug_userinfo(context: Context):
    await context.reply(f"triggering user is {context.user.nickname}, {context.user.hostname}")
    await context.reply(f"user identifed?: {context.user.identified}")


@command("superPing!")
@require_channel
@require_permission(TECHRAT)
async def cmd_superping(context: Context):
    await context.reply("pong!")

