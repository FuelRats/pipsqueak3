"""
deletion_management.py - commands for managing deletion marking on cases.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import asyncio
import uuid
from typing import Optional

from ..packages.commands import command
from ..packages.context.context import Context
from ..packages.mark_for_deletion import MarkForDeletion
from ..packages.permissions.permissions import require_permission, RAT, OVERSEER, require_channel
from ..packages.rescue import Rescue
from ..packages.utils import Status


# User input validation helper
def _validate(ctx: Context, validate: str) -> Optional[Rescue]:
    try:
        if validate not in ctx.bot.board:
            rescue = ctx.bot.board[int(ctx.words[1])]
        else:
            rescue = ctx.bot.board.get(ctx.words[1])
    except (KeyError, ValueError):
        try:
            force_uuid = uuid.UUID(ctx.words[1])
        except ValueError:
            return None
        else:
            rescue = ctx.bot.board.get(force_uuid)

    return rescue


@require_channel
@require_permission(RAT)
@command("md", "mdadd")
async def del_management_md(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !md <Client Name|Board Index> <Reason for Deletion>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    if not rescue.marked_for_deletion.marked:
        new_MFD = MarkForDeletion(marked=True, reporter=ctx.user.nickname, reason=ctx.words_eol[2])
    else:
        await ctx.reply(f"{rescue.client}'s case is already marked for deletion.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.marked_for_deletion = new_MFD
        case.status = Status.CLOSED
        await ctx.reply(f"{case.client}'s case has been closed and added to the MFD list.")

    await ctx.bot.board.remove_rescue(rescue)


@require_channel
@require_permission(OVERSEER)
@command("mdlist")
async def del_management_mdlist(ctx: Context):
    await ctx.reply("Marked for Deletion List:")

    for rescue in ctx.bot.board.values():
        if rescue.marked_for_deletion.marked:
            await ctx.reply(
                f"[@{rescue.api_id}] {rescue.client} {rescue.platform.value if rescue.platform else ''} "
                f"Reason: {rescue.marked_for_deletion.reason}, "
                f"Reporter: {rescue.marked_for_deletion.reporter}")
            await asyncio.sleep(delay=0.5)

    await ctx.reply("(End of Marked for Deletion list)")
