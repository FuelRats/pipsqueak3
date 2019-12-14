"""
case_management.py - Case management commands for interaction on IRC.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from loguru import logger

from src.config import PLUGIN_MANAGER
from src.packages.commands import command
from src.packages.context.context import Context
from src.packages.permissions.permissions import require_permission, RAT, TECHRAT, OVERSEER, ADMIN,\
    require_channel
from src.packages.utils import Platforms, Status, Formatting


@require_channel
@require_permission(RAT)
@command("active")
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
        logger.debug("cmd active: bad input")
        await ctx.reply("Usage: !active <Client Name|Case Number>")
        return

    rescue = ctx.bot.board.get(ctx.words[1])

    if not ctx.bot.board.get(ctx.words[1]):
        logger.debug("cmd active: rescue not found")
        await ctx.reply("No open case with that number or client name.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.active = not case.active
        await ctx.reply(f'{case.client}\'s case is now {Formatting.FORMAT_BOLD}'
                        f'{"Active" if case.active else "Inactive"}.')
