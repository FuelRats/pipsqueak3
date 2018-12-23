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
from Modules.permissions import require_permission, TECHRAT, require_channel
from Modules.rat_command import command
from database import DatabaseManager
from psycopg2 import sql

log = logging.getLogger(f"mecha.{__name__}")


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


@command("superPing!")
@require_channel
@require_permission(TECHRAT)
async def cmd_superping(context: Context):
    await context.reply("pong!")


@command("debug-fact")
@require_permission(TECHRAT)
async def cmd_query(context: Context):
    # assuming `database` is a instance of the DBM
    database = DatabaseManager()
    sql_query = sql.SQL("SELECT message from fact WHERE name=%s AND lang=%s")
    sql_values = (context.words[1], context.words[2])
    data = await database.query(sql_query, sql_values)
    for item in data:
        await context.reply(str(item))
