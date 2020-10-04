"""
debug.py - Debug and diagnostics commands

Provides IRC commands geared towards debugging mechasqueak itself.
This module should **NOT** be loaded in a production environment

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from uuid import UUID

from loguru import logger

from src.config import PLUGIN_MANAGER
from src.packages.commands import command
from src.packages.context.context import Context
from src.packages.fuelrats_api.v3 import UnauthorizedImpersonation
from src.packages.permissions.permissions import require_permission, TECHRAT, require_channel


@command("debug-whois")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_whois(context):
    """A debug command for running a WHOIS command.

    Returns
        str: string repreentation
    """
    data = await context.bot.whois(context.words[1])
    logger.debug(data)
    await context.reply(f"{data}")


@command("debug-userinfo")
@require_permission(TECHRAT)
@require_channel
async def cmd_debug_userinfo(context: Context):
    """
    A debug command for getting information about a user.
    """

    await context.reply(f"triggering user is {context.user.nickname}, {context.user.hostname}")
    await context.reply(
        f"user identified?: {context.user.identified} with account?: {context.user.account}")


@command("superPing!")
@require_channel
@require_permission(TECHRAT)
async def cmd_superping(context: Context):
    """
    A debug command to coerce mecha to respond.
    """

    await context.reply("pong!")


@command("getConfigPlugins")
@require_channel
@require_permission(TECHRAT)
async def cmd_get_plugins(context: Context):
    """Lists configuration plugins"""
    await context.reply(f"getting plugins...")

    plugins = PLUGIN_MANAGER.list_name_plugin()
    names = [plugin[0] for plugin in plugins]
    await context.reply(",".join(names))


@command("get_nickname_api")
@require_channel
@require_permission(TECHRAT)
async def cmd_get_nickname(context: Context):
    await context.reply("fetching....")
    result = await  context.bot.api_handler.get_rat("ClappersClappyton",
                                                    impersonation=context.user.account)
    await context.reply("got a result!")
    logger.debug("got nickname result {!r}", result)


@command("debug_ratid")
@require_channel
@require_permission(TECHRAT)
async def cmd_ratid(context: Context):
    target = context.words[-1]
    await context.reply(f"acquiring ratids for {target!r}...")
    api_rats = await context.bot.api_handler.get_rat(target, impersonation=context.user.account)
    if not api_rats:
        return await context.reply("go fish.")
    await context.reply(",".join([f"{rat.uuid}" for rat in api_rats]))


@command("debug_get_rat")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_get_rat(context: Context):
    target = context.words[-1]
    try:
        target = UUID(target)
    except ValueError:
        return await context.reply("invalid uuid.")
    await context.reply(f"fetching uuid {target}...")
    subject = await context.bot.api_handler.get_rat(target, impersonation=context.user.account)
    await context.reply(f"identified rats: {','.join(repr(obj.name) for obj in subject)}")


@command("debug_summoncase")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_summoncase(context: Context):
    await context.reply("summoning case....")
    rescue = await context.bot.board.create_rescue(client="some_client")
    something = await context.bot.api_handler.create_rescue(rescue, impersonating=context.user.account)
    await context.reply("done.")


@command("debug_fbr")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_fetch(context: Context):
    await context.reply("flushing my board and fetching...")
    keys = context.bot.board.keys()
    for key in list(keys):  # my keys now!
        await context.bot.board.remove_rescue(key)

    results = await context.bot.api_handler.get_rescues(context.user.nickname)

    await context.reply(f"{len(results)} open cases detected.")
    for rescue in sorted(results, key=lambda obj: obj.board_index if obj.board_index else 0):
        if rescue.board_index in context.bot.board:
            logger.warning("reassigning API imported rescue @{} a new board index (collision)",
                           rescue.api_id)
            rescue.board_index = None
        await context.bot.board.append(rescue)


@command("debug_fetch_rescue")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_fetch_single(context: Context):
    uid = UUID(context.words[-1])
    await context.reply(f"fetching @{uid}...")
    result = await context.bot.api_handler._get_rescue(uid, impersonation=context.user.account)
    if result:
        await context.reply("got a result")
    else:
        await context.reply("go fish.")


@command("debug_update_rescue")
@require_channel
@require_permission(TECHRAT)
async def cmd_update_rescue(context: Context):
    uid = UUID(context.words[-1])
    if uid not in context.bot.board:
        return await context.reply("not currently tracking that rescue?")
    rescue = context.bot.board[uid]
    await context.reply(f"updating @{uid}...")
    rescue.client = "some_test_client"
    try:
        # FIXME use account impersonation
        await context.bot.api_handler.update_rescue(rescue, impersonating=None)
    except UnauthorizedImpersonation:
        logger.exception("failed API action")
        return await context.reply("Action failed. Invoking IRC user is not authorized.")

    await context.reply("done.")


@command("debug_go_online")
@require_channel
@require_permission(TECHRAT)
async def cmd_debug_go_online(context: Context):
    await context.reply("going online...")
    context.bot.board.api_handler = context.bot.api_handler
    await context.bot.board.on_online()
