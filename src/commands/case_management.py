"""
case_management.py - Case management commands for interaction on IRC.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import datetime
import functools
import io
import itertools
import re
import typing
import uuid
from datetime import timezone

import humanfriendly
import pyparsing
from loguru import logger

from ._list_flags import ListFlags
from ..packages.commands import command
from ..packages.context.context import Context
from ..packages.epic import Epic
from ..packages.parsing_rules import (
    rescue_identifier,
    irc_name,
    suppress_first_word,
    timer,
    rest_of_line,
    platform,
)
from ..packages.permissions.permissions import (
    require_permission,
    RAT,
    OVERSEER,
    require_channel,
)
from ..packages.quotation.rat_quotation import Quotation
from ..packages.rat import Rat
from ..packages.rescue import Rescue
from ..packages.utils import Platforms, Status, color, bold, Colors

_TIME_RE = re.compile(r"(\d+)[: ](\d+)")
"""
Regex matcher used to find a time within a string. Used to determine
if a newly-submitted case is code red or not.
"""
ASSIGN_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    + pyparsing.OneOrMore(irc_name).setResultsName("rats")
)
ACTIVE_PATTERN = suppress_first_word + rescue_identifier.setResultsName("subject")

CLEAR_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    + pyparsing.Optional(irc_name).setResultsName("first_limpet")
)
CMDR_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    + rest_of_line.setResultsName("new_cmdr")
)

GRAB_PATTERN = suppress_first_word + rescue_identifier.setResultsName("subject")

IRC_NICK_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    + irc_name.setResultsName("new_nick")
)
JUST_RESCUE_PATTERN = suppress_first_word + rescue_identifier.setResultsName("subject")

SUB_CMD_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    + (pyparsing.Word(pyparsing.nums, pyparsing.nums, min=1) + pyparsing.WordEnd())
    .setParseAction(lambda token: int(token.quote_id[0]))
    .setResultsName("quote_id")
    + rest_of_line.setResultsName("remainder")
)

SYS_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    + rest_of_line.setResultsName("remainder")
)

TITLE_PATTERN = SYS_PATTERN

UNASSIGN_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    + pyparsing.OneOrMore(irc_name).setResultsName("rats")
)

INJECT_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    # The following group captures in any order (&).
    + (
        pyparsing.Optional(
            pyparsing.CaselessKeyword("cr") ^ pyparsing.CaselessKeyword("code red")
        ).setResultsName("code_red")
        & pyparsing.Optional(timer("timer"))
        & pyparsing.Optional(platform).setResultsName("platform")
    )
    # This comes positionally LAST and OUTSIDE the above capture group or it
    # catches the wrong things.
    + rest_of_line.setResultsName("remainder")
)

CODE_RED_PATTERN = suppress_first_word + rescue_identifier.setResultsName("subject")


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
    if not ACTIVE_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !active <Client Name|Case Number>")
        return
    tokens = ACTIVE_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])

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
    if not ASSIGN_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !assign <Client Name|Case Number> <Rat 1> <Rat 2> <Rat 3>")
        return
    tokens = ASSIGN_PATTERN.parseString(ctx.words_eol[0])
    logger.debug("parsed assign tokens::{}", tokens)
    # Pass case to validator, return a case if found or None
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    # Get rats from input command
    rat_list = tokens.rats

    # Get client's IRC nick, otherwise use client name as entered
    rescue_client = rescue.irc_nickname if rescue.irc_nickname else rescue.client

    async with ctx.bot.board.modify_rescue(rescue.board_index) as case:
        logger.debug("assigning {!r} to case {}", rat_list, rescue.board_index)
        for name in rat_list:
            rat = Rat(name=name, uuid=None)
            await case.add_rat(rat)

            if rat.name in case.unidentified_rats:
                await ctx.reply(f"Warning: {name!r} is NOT identified.")

    await ctx.reply(
        f"{rescue_client}: Please add the following rat(s) to your friends list:"
        f' {", ".join(str(rat) for rat in rat_list)}'
    )


@require_channel
@require_permission(RAT)
@command("clear", "close")
async def cmd_case_management_clear(ctx: Context):
    if not CLEAR_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !clear <Client Name|Board Index> [First Limpet Sender]")
        return
    tokens = CLEAR_PATTERN.parseString(ctx.words_eol[0])
    # Pass case to validator, return a case if found or None
    rescue = ctx.bot.board.get(tokens.subject[0])

    first_limpet = tokens.first_limpet[0] if tokens.first_limpet else None

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    if not rescue.system:
        return await ctx.reply("Cannot comply: system not set.")
    if not rescue.platform:
        return await ctx.reply("Cannot comply: platform not set.")
    if first_limpet:
        if first_limpet in rescue.unidentified_rats:
            return await ctx.reply(f"Cannot comply: {first_limpet!r}  is unidentified.")

        if first_limpet not in rescue.rats:
            return await ctx.reply(f"Cannot comply: {first_limpet!r} is not assigned to this rescue")
    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.active = False
        case.status = Status.CLOSED
        if first_limpet:
            case.first_limpet = rescue.rats[first_limpet].uuid
            # TODO: Add paperwork call link here

    await ctx.bot.board.remove_rescue(rescue)

    await ctx.reply(f"Case {case.client} was cleared!")


@require_channel
@require_permission(RAT)
@command("cmdr", "commander")
async def cmd_case_management_cmdr(ctx: Context):
    if not CMDR_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !cmdr <Client Name|Board Index> <CMDR name>")
        return
    tokens = CMDR_PATTERN.parseString(ctx.words_eol[0])
    # Pass case to validator, return a case if found or None
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.client = tokens.new_cmdr.strip()
        await ctx.reply(f"Client for {case.board_index} is now CMDR {case.client}")


@require_channel
@require_channel(RAT)
@command("codered", "casered", "cr")
async def cmd_case_management_codered(ctx: Context):
    if not CODE_RED_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !codered <Client Name|Board Index>")
        return

    tokens = CODE_RED_PATTERN.parseString(ctx.words_eol[0])

    # Pass case to validator, return a case if found or None
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.code_red = not case.code_red
        if case.code_red:
            case: Rescue
            notifiers = {name for name in case.rats.keys()}
            notifiers.update({name for name in case.unidentified_rats.keys()})
            await ctx.reply(
                f"Code Red! {case.client} is on {bold(color('Emergency Oxygen!', Colors.RED))}"
            )
            if notifiers:
                await ctx.reply(f"{', '.join(notifiers)} this is {bold('YOUR')} case!")
        else:
            await ctx.reply(f"{case.client} is no longer a Code Red.")


@require_channel
@require_permission(OVERSEER)
@command("delete")
async def cmd_case_management_delete(ctx: Context):
    if len(ctx.words) < 2:
        await ctx.reply("Usage: !delete <API ID>")
        return

    # Validate we have UUID:
    try:
        requested_case = uuid.UUID(ctx.words[1])
    except ValueError:
        await ctx.reply("Invalid API ID.")
        return
    else:
        rescue = ctx.bot.board.get(requested_case)
        # TODO: if the case is not present on the board, present the request to the API
        #  and delete that case.

        await ctx.reply(f"Deleted case with id {str(rescue.api_id)} - THIS IS NOT REVERTIBLE!")
        # FIXME: Add proper method to delete a case from the board
        await ctx.bot.board.remove_rescue(rescue)


@require_channel
@require_permission(RAT)
@command("epic")
async def cmd_case_management_epic(ctx: Context):
    # This command may be depreciated, and not used.  It's left in only as an artifact, or
    # if that changes.
    await ctx.reply(
        "This command is no longer in use.  "
        "Please visit https://fuelrats.com/epic/nominate to nominate an epic rescue."
    )
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
        await ctx.reply(
            f"{case.client}'s rescue has been marked as an " f"EPIC tale by {ctx.user.nickname}!"
        )
        await ctx.reply(f"Description: {new_epic.notes}")


@require_channel
@require_permission(RAT)
@command("grab")
async def cmd_case_management_grab(ctx: Context):
    if not GRAB_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !grab <Client Name>")
        return
    tokens = GRAB_PATTERN.parseString(ctx.words_eol[0])
    # Pass case to validator, return a case if found or None
    rescue: Rescue = ctx.bot.board.get(tokens.subject[0])

    subject = rescue.irc_nickname.casefold() if rescue else ctx.words[1].casefold()
    logger.debug("checking for last message of irc nick {!r}...", subject)
    last_message = ctx.bot.last_user_message.get(subject)
    logger.debug("last_message = {!r}", last_message)
    if not last_message:
        return await ctx.reply(f"Cannot comply: {ctx.words[1]} has not spoken recently.")

    if not rescue:
        case = await ctx.bot.board.create_rescue(client=ctx.words[1])
        async with ctx.bot.board.modify_rescue(case) as case:
            case.add_quote(last_message)

        return await ctx.reply(f"{case.client}'s case opened with {last_message!r}")

    if ctx.words[1].casefold() in ctx.bot.last_user_message:
        last_message = ctx.bot.last_user_message[ctx.words[1].casefold()]
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
        await ctx.reply(
            f"{case.client}'s case updated with " f"{last_message!r} (Case {case.board_index})"
        )


@require_channel
@require_permission(RAT)
@command("inject")
async def cmd_case_management_inject(ctx: Context):
    if not INJECT_PATTERN.matches(ctx.words_eol[0]):
        logger.debug("pattern match failed.")
        await ctx.reply("Usage: !inject <Client Name|Board Index> <Text to Add>")
        return
    tokens = INJECT_PATTERN.parseString(ctx.words_eol[0])
    # Pass case to validator, return a case if found or None
    rescue = ctx.bot.board.get(tokens.subject[0])

    logger.debug("tokens: {!r}", tokens)
    # SPARK-223 failsafe
    if tokens.subject[0] != ctx.words[1]:
        # if the subject doesn't match
        return await ctx.reply("Invalid IRC nick for inject. Abort.")

    if not rescue and not isinstance(tokens.subject[0], int):
        logger.debug("creating rescue for {!r}", tokens.subject[0])
        rescue = await ctx.bot.board.create_rescue(client=tokens.subject[0])
        async with ctx.bot.board.modify_rescue(rescue) as case:
            case.add_quote(ctx.words_eol[2], ctx.user.nickname)

            # check specific capture groups for existence.
            if tokens.xbox:
                case.platform = Platforms.XB
            if tokens.playstation:
                case.platform = Platforms.PS
            if tokens.pc:
                case.platform = Platforms.PC

            # Check if either CR was explicitly stated or a timer token exists.
            if tokens.code_red or tokens.timer:
                case.code_red = True

            await ctx.reply(
                f"{case.client}'s case opened with: " f"{ctx.words_eol[2]}  (Case {case.board_index})"
            )

            if case.code_red:
                await ctx.reply(f"Code Red! {case.client} is on Emergency Oxygen!")

            return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.add_quote(ctx.words_eol[2], ctx.user.nickname)

    await ctx.reply(
        f"{case.client}'s case updated with: " f"'{ctx.words_eol[2]}' (Case {case.board_index})"
    )


@require_channel
@require_permission(RAT)
@command("ircnick", "nick", "nickname")
async def cmd_case_management_ircnick(ctx: Context):
    if not IRC_NICK_PATTERN.matches(ctx.words_eol[0]):
        return await ctx.reply("Usage: !ircnick <Client Name|Board Index> <New Client Name>")
    tokens = IRC_NICK_PATTERN.parseString(ctx.words_eol[0])
    # Pass case to validator, return a case if found or None
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    new_name = tokens.new_nick
    # sanity check that probably can never be reached.
    if not new_name:
        raise ValueError("new_name should be truthy.")

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.irc_nickname = new_name
        await ctx.reply(f"Set IRC Nickname to {case.irc_nickname!r}")

    if new_name.casefold() != rescue.client.casefold():
        await ctx.reply(
            f"Caution: IRC Nickname {new_name!r} does not match "
            f"CMDR Name {rescue.client.casefold()!r}."
        )


@require_channel
@require_permission(RAT)
@command("pc", "ps", "xb")
async def cmd_case_management_system(ctx: Context):
    if not JUST_RESCUE_PATTERN.matches(ctx.words_eol[0]):
        return await ctx.reply("Usage: !<pc|ps|xb> <Client Name|Board Index>")
    tokens = JUST_RESCUE_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.platform = getattr(Platforms, ctx.words[0].upper())
        await ctx.reply(f"{case.client}'s platform set to {case.platform.value}.")


@require_channel()
@require_permission(RAT)
@command("quote")
async def cmd_case_management_quote(ctx: Context):
    if not JUST_RESCUE_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !quote <Client Name|Board Index>")
        return

    tokens = JUST_RESCUE_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    created_timestamp = rescue.updated_at.strftime("%b %d %H:%M:%S UTC")

    header = f"{rescue:s@r}, updated {created_timestamp}"

    await ctx.reply(header)

    if rescue.quotes:
        for i, quote in enumerate(rescue.quotes):
            delta = humanfriendly.format_timespan(
                (datetime.datetime.now(tz=timezone.utc) - quote.updated_at),
                detailed=False,
                max_units=2,
            )
            quote_timestamp = f"{delta} ago"
            await ctx.reply(f"[{i}][{quote.author} ({quote_timestamp})] {quote.message}")


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

    header = (
        f"{rescue.client}'s case {rescue.board_index} at "
        f"{rescue.system if rescue.system else 'an unspecified system'}, "
        f"updated {created_timestamp}  "
        f"@{rescue.api_id}"
    )

    await ctx.reply(header)

    if rescue.quotes:
        for i, quote in enumerate(rescue.quotes):
            quote_timestamp = (
                humanfriendly.format_timespan(
                    (datetime.datetime.now(tz=timezone.utc) - quote.updated_at),
                    detailed=False,
                    max_units=2,
                )
                + " ago"
            )
            await ctx.reply(f"[{i}][{quote.author} ({quote_timestamp})] {quote.message}")


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
    if not SUB_CMD_PATTERN.matches(ctx.words_eol[0]):
        return await ctx.reply("Usage: !sub <Client Name|Board Index> <Quote Number> [New Text]")
    tokens = SUB_CMD_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    quote_id = tokens.quote_id

    if quote_id > len(rescue.quotes):
        await ctx.reply(f"Invalid quote index for case #{rescue.board_index}")
        return

    logger.debug("quote_id:={}, remainder:={}", quote_id, tokens.remainder)

    if tokens.remainder:
        if quote_id > len(rescue.quotes):
            # no such quote, bail out
            return await ctx.reply(f"no such quote by id {quote_id}")
        new_quote = Quotation(
            message=ctx.words_eol[3],
            last_author=ctx.user.nickname,
            author=rescue.quotes[quote_id].author,
            created_at=rescue.quotes[quote_id].created_at,
            updated_at=datetime.datetime.now(timezone.utc),
        )

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
    if not SYS_PATTERN.matches(ctx.words_eol[0]):
        return await ctx.reply("Usage: !sys <Client Name|Board Index> <New System>")
    tokens = SYS_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])
    if not tokens.remainder:
        return await ctx.reply("Usage: !sys <Client Name|Board Index> <New System>")

    if not rescue:
        return await ctx.reply("No case with that name or number.")

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.system = tokens.remainder
        await ctx.reply(f"{case.client}'s system set to {tokens.remainder!r}")


@require_channel
@require_permission(RAT)
@command("title")
async def cmd_case_management_title(ctx: Context):
    if not TITLE_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !title <Client Name|Board Index> <Operation Title")
        return

    tokens = TITLE_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.title = tokens.remainder
        await ctx.reply(f"{case.client}'s rescue title set to {tokens.remainder!r}")


@require_channel
@require_permission(RAT)
@command("unassign", "rm", "remove", "standdown")
async def cmd_case_management_unassign(ctx: Context):
    if not UNASSIGN_PATTERN.matches(ctx.words_eol[0]):
        return await ctx.reply("Usage: !unassign <Client Name|Case Number> <Rat 1> <Rat 2> <Rat 3>")

    tokens = UNASSIGN_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        return await ctx.reply("No case with that name or number.")

    # Get rats from input command
    rat_list = tokens.rats.asList()

    # Get client's IRC nick, otherwise use client name as entered
    rescue_client = rescue.irc_nickname if rescue.irc_nickname else rescue.client

    async with ctx.bot.board.modify_rescue(rescue.board_index) as case:
        removed_rats = []
        case: Rescue
        for each in rat_list:
            target = each.casefold()
            if target not in case.unidentified_rats and target not in case.rats:
                return await ctx.reply(f"Cannot comply: {target!r}. (Please check your spelling)")
            case.remove_rat(each.casefold())
            removed_rats.append(each)

        removed_rats_str = ", ".join(removed_rats)
        return await ctx.reply(f"Removed from {rescue_client}'s case: {removed_rats_str}")


def remainder(words: typing.Iterable[str]) -> str:
    return " ".join(words)


@command("list")
async def cmd_list(ctx: Context):
    """
    Implementation of !list

        Supported parameters:
        -i: Also show inactive (but still open) cases.
        -r: Show assigned rats
        -u: Show only cases with no assigned rats
        -@: Show full case IDs.  (LONG)

    Args:
        ctx:

    """
    _, *words = ctx.words

    flags = ListFlags()
    platform_filter = None

    # plain invocation
    if len(words) == 0:
        ...  # use above defaults (done this way so else can be used below as an error state)

    # arguments invocation
    elif len(words) == 1 or len(words) == 2:
        flags_set = False
        platform_filter_set = False

        for word in words:  # type: str
            if word.startswith("-"):
                if flags_set:
                    raise RuntimeError("invalid usage")  # FIXME: usage warning to user
                flags = ListFlags.from_word(word)
                flags_set = True
            else:
                # platform or bust
                if platform_filter_set:
                    raise RuntimeError("invalid usage")  # FIXME: usage error

                try:
                    platform_filter = Platforms[word.upper()]
                except KeyError:
                    return await ctx.reply(f"unrecognized platform '{word.upper()}'")

    else:
        raise RuntimeError  # FIXME: usage error
    logger.debug(f"flags set:= {flags} \t platform_filter := {platform_filter}")
    active_rescues: typing.List[Rescue] = []
    inactive_rescues: typing.List[Rescue] = []

    rescue_filter = functools.partial(_rescue_filter, flags, platform_filter)

    # for each rescue that doesn't matches the filter
    for rescue in itertools.filterfalse(rescue_filter, iter(ctx.bot.board.values())):  # type: Rescue
        # put it in the right list
        if rescue.active:
            active_rescues.append(rescue)
        else:
            inactive_rescues.append(rescue)
    format_specifiers = "c"
    if flags.show_assigned_rats:
        format_specifiers += "r"
    if flags.show_uuids:
        format_specifiers += "@"

    if not active_rescues:
        await ctx.reply("No active rescues.")
    else:

        output = _list_rescue(active_rescues, format_specifiers)
        if output:
            await ctx.reply(output)
    if flags.show_inactive:
        if not inactive_rescues:
            return await ctx.reply("No inactive rescues.")

        output = _list_rescue(inactive_rescues, format_specifiers)
        if output:
            await ctx.reply(output)


def _list_rescue(rescue_collection, format_specifiers):
    buffer = io.StringIO()
    buffer.write(f"{len(rescue_collection)} active cases. ")
    for rescue in rescue_collection:
        buffer.write(format(rescue, format_specifiers))
        buffer.write("\n")
    output = buffer.getvalue()
    return output.rstrip("\n")


def _rescue_filter(
    flags: ListFlags, platform_filter: typing.Optional[Platforms], rescue: Rescue
) -> bool:
    """
    determine whether the `rescue` object is one we care about

    Args:
        rescue:

    Returns:

    """
    filters = []

    if flags.filter_unassigned_rescues:
        # return whether any rats are assigned
        # either properly or via unidentified rats
        filters.append(bool(rescue.rats) or bool(rescue.unidentified_rats))

    # use the active bool on rescue if we don't want inactives, otherwise True
    filters.append(rescue.active if not flags.show_inactive else True)

    if platform_filter:  # if we rae filtering on platform
        filters.append(rescue.platform is platform_filter)
    return not all(filters)
