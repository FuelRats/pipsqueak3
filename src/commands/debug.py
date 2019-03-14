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
