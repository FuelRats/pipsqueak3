"""
case_management.py - Case management commands for interaction on IRC.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import datetime
import re
import uuid
from datetime import timezone
from typing import Optional

import humanfriendly

from ..packages.commands import command
from ..packages.context.context import Context
from ..packages.epic import Epic
from ..packages.permissions.permissions import require_permission, RAT, OVERSEER, require_channel
from ..packages.quotation.rat_quotation import Quotation
from ..packages.rat import Rat
from ..packages.rescue import Rescue
from ..packages.utils import Platforms, Status

_TIME_RE = re.compile(r'(\d+)[: ](\d+)')


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
        for name in rat_list:
            await case.add_rat(Rat(name=name, uuid=None))

            if name in case.unidentified_rats:
                await ctx.reply(f"Warning: {name!r} is NOT identified.")

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
    await ctx.bot.board.remove_rescue(rescue)

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


@require_channel
@require_permission(RAT)
@command("epic")
async def cmd_case_management_epic(ctx: Context):
    # This command may be depreciated, and not used.  It's left in only as an artifact, or
    # if that changes.
    await ctx.reply("This command is no longer in use.  "
                    "Please visit https://fuelrats.com/epic/nominate to nominate an epic rescue.")
    return
    # End Depreciation warning

    if len(ctx.words) < 3:
        await ctx.reply("Usage: !epic <Client Name|Board Index> <Description>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    if rescue.epic:
        await ctx.reply(f"{rescue.client}'s case is already considered an epic tale.")
        return

    new_epic = Epic(uuid=rescue.api_id, notes=ctx.words_eol[2], rescue=rescue)
    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.epic.append(new_epic)
        await ctx.reply(f"{case.client}'s rescue has been marked as an "
                        f"EPIC tale by {ctx.user.nickname}!")
        await ctx.reply(f"Description: {new_epic.notes}")


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
            case.add_quote(ctx.words_eol[2], ctx.user.nickname)

            for keyword in ctx.words_eol[2].split():
                if keyword in {item.value for item in Platforms}:
                    case.platform = Platforms[keyword]
                if keyword.casefold() == "cr" or "code red" in keyword.casefold() \
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


@require_channel()
@require_permission(RAT)
@command("quote")
async def cmd_case_management_quote(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !quote <Client Name|Board Index>")
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
            quote_timestamp = humanfriendly.format_timespan((datetime.datetime.now(tz=timezone.utc)
                                                             - quote.updated_at),
                                                            detailed=False, max_units=2) + " ago"
            await ctx.reply(f'[{i}][{quote.author} ({quote_timestamp})] {quote.message}')


@require_channel()
@require_permission(OVERSEER)
@command("quoteid")
async def cmd_case_management_quoteid(ctx: Context):
    # TODO: Remove NYI Message when API capability is ready.
    await ctx.reply("Use !quote.  API is not available in offline mode.")
    return

    if len(ctx.words) != 2:
        await ctx.reply("Usage: !quoteid <API ID>")
        return

    # Pass case to validator, return a case if found or None

    # TODO: Make API Call, returning rescue matching API ID requested.
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that ID.")
        return

    created_timestamp = rescue.updated_at.strftime("%b %d %H:%M:%S UTC")

    header = f"{rescue.client}'s case {rescue.board_index} at " \
             f"{rescue.system if rescue.system else 'an unspecified system'}, " \
             f"updated {created_timestamp}  " \
             f"@{rescue.api_id}"

    await ctx.reply(header)

    if rescue.quotes:
        for i, quote in enumerate(rescue.quotes):
            quote_timestamp = humanfriendly.format_timespan((datetime.datetime.now(tz=timezone.utc)
                                                             - quote.updated_at),
                                                            detailed=False, max_units=2) + " ago"
            await ctx.reply(f'[{i}][{quote.author} ({quote_timestamp})] {quote.message}')


@require_channel()
@require_permission(OVERSEER)
@command("reopen")
async def cmd_case_management_reopen(ctx: Context):
    # TODO: Add Re-open command with API pass
    await ctx.reply("Not available in offline mode.")
    return


@require_channel()
@require_permission(OVERSEER)
@command("sub")
async def cmd_case_management(ctx: Context):
    if len(ctx.words) < 3:
        await ctx.reply("Usage: !sub <Client Name|Board Index> <Quote Number> [New Text]")

    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    try:
        quote_id = int(ctx.words[2])
    except (TypeError, ValueError):
        await ctx.reply(f"{ctx.words[2]!r} is not a valid quote index.")
        return

    if quote_id > len(rescue.quotes):
        await ctx.reply(f"Invalid quote index for case #{rescue.board_index}")
        return

    if len(ctx.words_eol[1].split()) > 3:
        new_quote = Quotation(message=ctx.words_eol[2],
                              last_author=ctx.user.nickname,
                              author=rescue.quotes[quote_id].author,
                              created_at=rescue.quotes[quote_id].created_at,
                              updated_at=datetime.datetime.now(timezone.utc))

        async with ctx.bot.board.modify_rescue(rescue) as case:
            case.quotes[quote_id] = new_quote
            await ctx.reply(f"Updated line {quote_id}.")
            return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        del case.quotes[quote_id]
        await ctx.reply(f"Deleted line {quote_id}.")


@require_channel
@require_permission(RAT)
@command("sys", "loc", "location")
async def cmd_case_management(ctx: Context):
    if len(ctx.words) < 3:
        return await ctx.reply("Usage: !sys <Client Name|Board Index> <New System>")

    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        return await ctx.reply("No case with that name or number.")

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.system = ctx.words_eol[2]
        await ctx.reply(f"{case.client}'s system set to {ctx.words_eol[2]!r}")


@require_channel
@require_permission(RAT)
@command("title")
async def cmd_case_management_title(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !title <Client Name|Board Index> <Operation Title")
        return

    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.title = ctx.words_eol[3]
        await ctx.reply(f"{case.client}'s rescue title set to {ctx.words_eol[2]!r}")


@require_channel
@require_permission(RAT)
@command("unassign", "rm", "remove", "standdown")
async def cmd_case_management_assign(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !unassign <Client Name|Case Number> <Rat 1> <Rat 2> <Rat 3>")
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
        removed_rats = []
        for each in rat_list:
            case.remove_rat(each.casefold())
            removed_rats.append(each)

        removed_rats_str = " ,".join(removed_rats)
        await ctx.reply(f"{removed_rats_str} are directed to stand down. (Unassigned from case)")


@require_channel
@require_permission(RAT)
@command("xb")
async def cmd_case_management_xb(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !xb <Client Name|Board Index>")
        return

    # Pass case to validator, return a case if found or None
    rescue = _validate(ctx, ctx.words[1])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.platform = Platforms.PC
        await ctx.reply(f"{case.client}'s platform set to XB.")
