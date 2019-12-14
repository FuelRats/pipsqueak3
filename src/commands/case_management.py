"""
case_management.py - Case management commands for interaction on IRC.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import uuid

from loguru import logger

from src.config import PLUGIN_MANAGER
from src.packages.commands import command
from src.packages.context.context import Context
from src.packages.permissions.permissions import require_permission, RAT, TECHRAT, OVERSEER, ADMIN,\
    require_channel
from src.packages.utils import Platforms, Status, Formatting


@require_channel
@require_permission(RAT)
@command("active", "activate", "inactive", "deactivate")
async def cmd_case_management_active(ctx: Context):
    """
    Toggles the indicated case as active or inactive.  Requires an OPEN case.

    Usage: !active 2|ClientName

    Example:    !active 2
                !active Concordance12

    Channel Only: YES
    Permission: Rat
    """
    if len(ctx.words) != 2:
        await ctx.reply("Usage: !active <Client Name|Case Number>")
        return

    try:
        if ctx.words[1] not in ctx.bot.board:
            rescue = ctx.bot.board[int(ctx.words[1])]
        else:
            rescue = ctx.bot.board.get(ctx.words[1])
    except (KeyError, ValueError):
        try:
            force_uuid = uuid.UUID(ctx.words[1])
        except ValueError:
            await ctx.reply("No case with that name or number.")
            return
        else:
            rescue = ctx.bot.board.get(force_uuid)

    # We either have a valid case or we've left the method at this point.
    async with ctx.bot.board.modify_rescue(rescue.board_index) as case:
        case.active = not case.active
        await ctx.reply(f'{case.client}\'s case is now {"Active" if case.active else "Inactive"}.')


@require_channel
@require_permission(RAT)
@command("assign", "add", "go")
async def cmd_case_management_assign(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !assign <Client Name|Case Number> <Rat 1> <Rat 2> <Rat 3>")
        return

    # validate client/case/UUID
    try:
        if ctx.words[1] not in ctx.bot.board:
            rescue = ctx.bot.board[int(ctx.words[1])]
        else:
            rescue = ctx.bot.board.get(ctx.words[1])
    except (KeyError, ValueError):
        try:
            force_uuid = uuid.UUID(ctx.words[1])
        except ValueError:
            await ctx.reply("No case with that name or number.")
            return
        else:
            rescue = ctx.bot.board.get(force_uuid)

    # Get rats from input command
    rat_list = ctx.words_eol[2].split()

    # Get client's IRC nick, otherwise use client name as entered
    rescue_client = rescue.irc_nickname if rescue.irc_nickname else rescue.client

    async with ctx.bot.board.modify_rescue(rescue.board_index) as case:
        for rat in rat_list:
            # TODO Perform Rat Validation here (assign)
            if rat not in case.rats:
                case.rats.append(rat)
            else:
                await ctx.reply(f"{rat} is already assigned to case {case.board_index}.")
                return

    await ctx.reply(f'{rescue_client}: Please add the following rat(s) to your friends list:'
                    f' {", ".join(str(rat) for rat in rat_list)}')


@require_channel
@require_permission(RAT)
@command("clear", "close")
async def cmd_case_management_clear(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !clear <Client Name|Board Index> [First Limpet Sender]")
        return

        # validate client/case/UUID
    try:
        if ctx.words[1] not in ctx.bot.board:
            rescue = ctx.bot.board[int(ctx.words[1])]
        else:
            rescue = ctx.bot.board.get(ctx.words[1])
    except (KeyError, ValueError):
        try:
            force_uuid = uuid.UUID(ctx.words[1])
        except ValueError:
            await ctx.reply("No case with that name or number.")
            return
        else:
            rescue = ctx.bot.board.get(force_uuid)

    async with ctx.bot.board.modify_rescue(rescue.board_index) as case:
        pass