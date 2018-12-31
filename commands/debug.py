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
from Modules.galaxy import Galaxy
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


@command("search")
@require_permission(TECHRAT)
async def cmd_search(context: Context):
    galaxy = Galaxy()
    data = await galaxy.find_system_by_name(context.words_eol[1])
    if data:
        response = f"{data.name} is a {data.spectral_class}-class star."
        response += f" It is located at ({data.position.x}, {data.position.y}, {data.position.z})."
        if data.is_populated:
            response += f" It is populated."
        else:
            response += f" It is not populated."
        await context.reply(response)
    else:
        await context.reply("That system could not be found.")


@command("fuzzy")
@require_permission(TECHRAT)
async def cmd_fuzzy(context: Context):
    galaxy = Galaxy()
    data = await galaxy.search_systems_by_name(context.words_eol[1])
    if data:
        await context.reply(', '.join(data))
    else:
        await context.reply("Could not find any systems with similar names!")


@command("plot")
@require_permission(TECHRAT)
async def cmd_plot(context: Context):
    galaxy = Galaxy()
    args = context.words_eol[1].split(',')
    data = await galaxy.plot_waypoint_route(args[0].strip(), args[1].strip())
    if data:
        await context.reply(', '.join(data))
    else:
        await context.reply("Could not plot that route.")


@command("scoopable")
@require_permission(TECHRAT)
async def cmd_scoopable(context: Context):
    galaxy = Galaxy()
    data = await galaxy.find_nearest_scoopable(context.words_eol[1])
    if data:
        await context.reply(f"{data.name}, {data.spectral_class}-class")
    else:
        await context.reply(f"Could not find any scoopables nearby.")
