"""
facts.py - IRC Commands for the Fact Manager.

Provides IRC commands to manage the Facts database.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging

from Modules.context import Context
from Modules.permissions import require_permission, TECHRAT, OVERSEER, RAT, require_channel
from Modules.rat_command import command
from Modules.fact_manager import FactManager, Fact
from psycopg2 import sql

log = logging.getLogger(f"mecha.{__name__}")


@command("factadd", "fact-add")
@require_permission(OVERSEER)
async def cmd_fm_factadd(context: Context):
    """
    Adds a new fact to the database, with timestamp and invoker as creator,
    creating a transaction log in the process.

    !factadd <name> <langID> <message>
    """
    await context.reply("Not Yet Implemented. Sorry!")


@command("factdel", "fact-del")
@require_permission(TECHRAT)
async def cmd_fm_factdel(context: Context):
    """
    Deletes a fact marked for deletion, creating a transaction log in the process.

    !factdel <name> <langID>
    """
    await context.reply("Not Yet Implemented. Sorry!")


@command("factalias", "fact-alias")
@require_permission(OVERSEER)
async def cmd_fm_factalias(context: Context):
    """
    Adds/Removes aliases for existing facts.

    !factalias add <base fact> <alias>
    !factalias del <base fact> <alias>
    """
    await context.reply("Not Yet Implemented. Sorry!")


@command("factdetail", "fact-detail")
@require_permission(RAT)
async def cmd_fm_factdetail(context: Context):
    """
    Detailed fact information, per fact.

    !factdetail <name> <langID>
    """
    await context.reply("Not Yet Implemented. Sorry!")


@command("factmfd", "fact-mfd")
@require_permission(OVERSEER)
async def cmd_fm_factmfd(context: Context):
    """
    Marks a fact for deletion.
    !factmfd <name> <langID>
    """
    await context.reply("Not Yet Implemented. Sorry!")


@command("facthistory", "fact-history")
@require_permission(OVERSEER)
async def cmd_fm_facthistory(context: Context):
    """
    Detailed history of fact and revisions.
    !facthistory <name> <langID>
    """
    await context.reply("Not Yet Implemented. Sorry!")
