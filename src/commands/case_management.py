"""
case_management.py - Case management commands for interaction on IRC.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import datetime
from datetime import tzinfo
import humanfriendly

import uuid
import re
from loguru import logger

from src.config import PLUGIN_MANAGER
from src.packages.commands import command
from src.packages.context.context import Context
from src.packages.permissions.permissions import require_permission, RAT, TECHRAT, OVERSEER, ADMIN,\
    require_channel
from src.packages.utils import Platforms, Status, Formatting
from src.packages.rescue import Rescue
from src.packages.utils import ratlib
from typing import Optional

_TIME_RE = re.compile('(\d+)[: ](\d+)')


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

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    # We either have a valid case or we've left the method at this point.
    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.active = not case.active
        await ctx.reply(f'{case.client}\'s case is now {"Active" if case.active else "Inactive"}.')


@require_channel
@require_permission(RAT)
@command("assign", "add", "go")
async def cmd_case_management_assign(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !assign <Client Name|Case Number> <Rat 1> <Rat 2> <Rat 3>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

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
    if len(ctx.words) > 2:
        await ctx.reply("Usage: !clear <Client Name|Board Index> [First Limpet Sender]")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    # Only set First Limpet if it was specified.
    if len(ctx.words) == 3:
        first_limpet = ctx.words[2]
    else:
        first_limpet = ""

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.active = False
        case.status = Status.CLOSED
        if first_limpet:
            case.first_limpet = first_limpet
            # TODO: Add paperwork call link here

    # FIXME: Deleting case from the board, as we don't have a proper method yet.
    del ctx.bot.board[rescue.board_index]

    await ctx.reply(f"Case {case.client} was cleared!")


@require_channel
@require_permission(RAT)
@command("cmdr", "commander")
async def cmd_case_management_cmdr(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !cmdr <Client Name|Board Index> <CMDR name>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.client = ctx.words[2]
        await ctx.reply(f"Client for {case.board_index} is now CMDR {case.client}")


@require_channel
@require_channel(RAT)
@command("codered", "casered", "cr")
async def cmd_case_management_codered(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !codered <Client Name|Board Index>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.code_red = not case.code_red
        if case.code_red:
            await ctx.reply(f"Code Red! {case.client} is on Emergency Oxygen!")
        else:
            await ctx.reply(f"{case.client} is no longer a Code Red.")


@require_channel
@require_permission(OVERSEER)
@command("delete")
async def cmd_case_management_delete(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !delete <Database ID>")
        return

    # Validate we have UUID:
    try:
        requested_case = uuid.UUID(ctx.words[1])
    except ValueError:
        await ctx.reply("Invalid Database ID.")
        return
    else:
        rescue = ctx.bot.board.get(requested_case)
        # TODO: if the case is not present on the board, present the request to the API
        #  and delete that case.

        await ctx.reply(f"Deleted case with id {str(rescue.api_id)} - THIS IS NOT REVERTIBLE!")
        # FIXME: Add proper method to delete a case from the board
        del ctx.bot.board[requested_case]


# TODO: !Epic

# TODO: !grab
@require_channel
@require_permission(RAT)
@command("grab")
async def cmd_case_management_grab(ctx: Context):
    if len(ctx.words) != 2:
        await ctx.reply("Usage: !grab <Client Name>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        async with ctx.bot.board.create_rescue() as case:
            case.add_quote()
        return

    if ctx.words[1].casefold() in ctx.bot.last_user_message:
        last_message = ctx.bot.last_user_message[ctx.words[1]]
    elif int(ctx.words[1]) in ctx.bot.board:
        if rescue.client.casefold() in ctx.bot.last_user_message:
            last_message = ctx.bot.last_user_message[rescue.client.casefold()]
        else:
            await ctx.reply("Nothing to grab from that client.")
            return
    else:
        await ctx.reply("Nothing to grab from that client.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.add_quote(last_message, ctx.words[1].casefold())
        await ctx.reply(f"{case.client}'s case updated with "
                        f"{last_message!r} (Case {case.board_index})")


@require_channel
@require_permission(RAT)
@command("inject")
async def cmd_case_management_inject(ctx: Context):
    if len(ctx.words) < 3:
        await ctx.reply("Usage: !inject <Client Name|Board Index> <Text to Add>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        rescue = await ctx.bot.board.create_rescue(client=ctx.words[1])
        async with ctx.bot.board.modify_rescue(rescue) as case:
            case.add_quote(ctx.user.nickname, ctx.words_eol[2])

            for keyword in ctx.words_eol[2].split():
                if keyword in [item.value for item in Platforms]:
                    case.platform = Platforms[keyword]
                if keyword.casefold() == "cr" or "code red" in ctx.words_eol[2].casefold()\
                        or _TIME_RE.match(ctx.words_eol[2]):
                    case.code_red = True

            await ctx.reply(f"{case.client}'s case opened with: "
                            f"{ctx.words_eol[1]}  (Case {case.board_index})")

            if case.code_red:
                await ctx.reply(f"Code Red! {case.client} is on Emergency Oxygen!")

            return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.add_quote(ctx.words_eol[2], ctx.user.nickname)

    await ctx.reply(f"{case.client}'s case updated with: "
                    f"'{ctx.words_eol[2]}' (Case {case.board_index})")


@require_channel
@require_permission(RAT)
@command("ircnick", "nick", "nickname")
async def cmd_case_management_ircnick(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !ircnick <Client Name|Board Index> <New Client Name>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    new_name = ctx.words[2]

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.irc_nickname = new_name
        await ctx.reply(f"Set IRC Nickname to {case.irc_nickname!r}")

    if new_name.casefold() != rescue.client.casefold():
        await ctx.reply("Caution: IRC Nickname does not match CMDR Name.")


@require_channel
@require_permission(RAT)
@command("pc")
async def cmd_case_management_pc(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !pc <Client Name|Board Index>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.platform = Platforms.PC
        await ctx.reply(f"{case.client}'s platform set to PC.")


@require_channel
@require_permission(RAT)
@command("ps")
async def cmd_case_management_ps(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !ps <Client Name|Board Index>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.platform = Platforms.PS
        await ctx.reply(f"{case.client}'s platform set to Playstation.")


# TODO: !pwn

@require_channel()
@require_permission(RAT)
@command("quote")
async def cmd_case_management_quote(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !quote <Client Name|Board Index")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    created_timestamp = rescue.updated_at.strftime("%b %d %H:%M:%S UTC")

    header = f"{rescue.client}'s case {rescue.board_index} at " \
             f"{rescue.system if rescue.system else 'an unspecified system'}, " \
             f"updated {created_timestamp}  " \
             f"@{rescue.api_id}"

    await ctx.reply(header)

    if rescue.quotes:
        for i, quote in enumerate(rescue.quotes):
            # FIXME: Quote dates are not set properly on the Quotation object,
            #  so the timestamp is useless.
            # quote_timestamp = humanfriendly.format_timespan((datetime.datetime.utcnow()
            #                                                 - quote.updated_at),
            #                                                detailed=False,
            #                                                max_units=2) + " ago"
            # await ctx.reply(f'[{i}][{quote.author} ({quote_timestamp})] {quote.message}')
            await ctx.reply(f'[{i}][{quote.author}] {quote.message}')
