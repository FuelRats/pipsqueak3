"""
Diagnostics.py - Diagnostics module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

"""

import logging
from datetime import datetime

import IPython

import config
from Modules import permissions
from Modules.commandcontext import CommandContext
from Modules.permissions import require_permission
from Modules.rat_command import Commands

log = logging.getLogger(f'{config.Logging.base_logger}.handlers')


@require_permission(permissions.TECHRAT)
@Commands.command("debug-fetch")
async def cmd_testNick(bot, trigger: CommandContext):
    """
    retrieves the invoking user from the bot's user listing and dumps it to the log file
    """
    irc_user = bot.users[trigger.user.nickname]
    log.debug(f"detected user is {trigger.user.nickname} with data {irc_user}")
    await trigger.reply("Done. see logs.")


@require_permission(permissions.TECHRAT)
@Commands.command("debug-whois")
async def cmd_whois(bot, trigger: CommandContext):
    """
    Finds a specified user via a WHOIS command,
            and returns the data to the log file
    """
    nickname = trigger.words[1]
    start = datetime.utcnow()
    log.debug(f"nickname= '{nickname}'")
    data = await bot.whois(nickname)
    end = datetime.utcnow()
    log.info(data)

    await trigger.reply(f"done in {end-start}.")


@require_permission(permissions.TECHRAT)
@Commands.command("divideByZero")
async def cmd_divide_by_zero(*args):
    """divides by zero, for science!"""
    return 0 / 0


@require_permission(permissions.TECHRAT, override_message="Just no.")
@Commands.command("debug-console")
async def cmd_console(bot, trigger):
    """
    Creates a console in the current context
    WARNING: running this console will cause a timeout in 180 seconds if it is not closed.
     - unless we can come up with a  way of making this not block.
    """
    # IPython.start_ipython(argv=[])
    await IPython.embed()
