"""
administration.py  -- administration commands

This module contains commands specific to administering the bot.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging

from src.config import setup
from src.packages.cli_manager import cli_manager
from src.packages.commands import command
from src.packages.context import Context
from src.packages.permissions import require_channel, require_permission, TECHRAT

LOG = logging.getLogger(f"mecha.{__name__}")


@command("rehash")
@require_channel(message="please do this where everyone can see 😒")
@require_permission(TECHRAT, override_message="no.")
async def cmd_rehash(context: Context):
    """ rehash the hash browns. (reloads config file)"""
    LOG.warning(f"config rehashing invoked by user {context.user.nickname}")
    path = cli_manager.GET_ARGUMENTS().config_file
    await context.reply(f"reloading configuration...")
    try:
        _, resulting_hash = setup(path)
    except (KeyError, ValueError) as exc:
        # emit stacktrace to logfile
        LOG.exception("failed to rehash configuration.")
        # if you have access to mecha's configuration file, you have access to its logs.
        # no need to defer this to the top-level exception handler.
        await context.reply(f"unable to rehash configuration file see logfile for details.")

    else:
        # no errors, respond status OK with the first octet of the hash.
        await context.reply(f"rehashing completed successfully. ({resulting_hash[:8]}) ")
