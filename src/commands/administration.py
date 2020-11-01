"""
administration.py  -- administration commands

This module contains commands specific to administering the bot.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from importlib import metadata

from loguru import logger

from ..config import setup
from ..packages.cli_manager import cli_manager
from ..packages.commands import command
from ..packages.context import Context
from ..packages.permissions import TECHRAT, RECRUIT


@command(
    "rehash",
    require_channel=True,
    override_channel_message="please do this where everyone can see 😒",
    require_permission=TECHRAT,
    require_permission_message="no.",
)
async def cmd_rehash(context: Context):
    """ rehash the hash browns. (reloads config file)"""
    logger.warning(f"config rehashing invoked by user {context.user.nickname}")
    path = cli_manager.GET_ARGUMENTS().config_file
    await context.reply(f"reloading configuration...")
    try:
        _, resulting_hash = setup(path)
    except (KeyError, ValueError) as exc:
        # emit stacktrace to logfile
        logger.exception("failed to rehash configuration.")
        # if you have access to mecha's configuration file, you have access to its logs.
        # no need to defer this to the top-level exception handler.
        await context.reply(f"unable to rehash configuration file see logfile for details.")

    else:
        # no errors, respond status OK with the first octet of the hash.
        await context.reply(f"rehashing completed successfully. ({resulting_hash[:8]}) ")


@command("version", require_permission=RECRUIT)
async def cmd_version(ctx: Context):
    try:
        return await ctx.reply(f"SPARK version {metadata.version('pipsqueak3')}")
    except metadata.PackageNotFoundError:
        return await ctx.reply("SPARK version ?.?.? (dirty)")
