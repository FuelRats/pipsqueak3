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
from Modules.fact_manager import FactManager, Fact
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
    sql_query = sql.SQL("SELECT message from fact2 WHERE name=%s AND lang=%s")
    sql_values = (context.words[1], context.words[2])
    data = await database.query(sql_query, sql_values)
    if not data:
        await context.reply("No fact matched query.")
    else:
        for item in data:
            await context.reply(str(item))


@command("fm-find")
@require_permission(TECHRAT)
async def cmd_fm_find(context: Context):
    fm = FactManager()
    result = Fact()
    result = await fm.find(context.words[1], context.words[2])

    await context.reply(f"Name: {result.name}")
    await context.reply(f"Message: {result.message}")
    await context.reply(f"Author: {result.author}")


@command("fm-add")
@require_permission(TECHRAT)
async def cmd_fm_add(context: Context):
    new_fact = Fact(name='insert',
                    lang='en',
                    author='Shatt',
                    message='This is a test fact inserted by debug command.',
                    editedby='Shatt',
                    mfd=False)
    fm = FactManager()
    await fm.add(new_fact)
    await context.reply("Debug Fact Added.")
