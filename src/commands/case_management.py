"""
case_management.py - Case management commands for interaction on IRC.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import functools
import io
import itertools
import re
import typing
import uuid
import warnings
import pendulum
import humanfriendly
import pyparsing
from loguru import logger

from ..templates import RescueRenderFlags, template_environment
from ..packages.commands import command
from ..packages.context.context import Context
from ..packages.parsing_rules import (
    rescue_identifier,
    irc_name,
    suppress_first_word,
    timer,
    rest_of_line,
    platform,
    api_id,
)
from ..packages.permissions.permissions import (
    RAT,
    OVERSEER,
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

ACTIVE_PATTERN = (
    suppress_first_word
    + rescue_identifier.setResultsName("subject")
    # This comes positionally LAST or it catches the wrong things.
    + rest_of_line.setResultsName("remainder")
)

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

REOPEN_PATTERN = suppress_first_word + api_id.setResultsName("subject")


@command("active", "activate", "inactive", "deactivate", require_permission=RAT, require_channel=True)
async def cmd_case_management_active(ctx: Context):
    """
    Toggles the indicated case as active or inactive.  Requires an OPEN case.

    Usage: !active 2|ClientName [OptionalInjectMessage]

    Example:    !active 2
                !active Concordance12 The client left IRC without communication

    Channel Only: YES
    Permission: Rat
    """
    if not ACTIVE_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !active <Client Name|Case Number> [Optional inject message]")
        return
    tokens = ACTIVE_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    # We either have a valid case or we've left the method at this point.
    async with ctx.bot.board.modify_rescue(rescue, impersonation=ctx.user.account) as case:
        logger.debug(f"Switching case to active = {not case.active}")
        case.active = not case.active
        logger.debug(f"Inject message: {tokens.remainder}")
        if tokens.remainder.lstrip(" "):
            # Inject message before toggling active/inactive if it is passed
            case.add_quote(tokens.remainder, ctx.user.nickname)
            await ctx.reply(
                f"{case.client}'s case updated with: {tokens.remainder!r} (Case {case.board_index})"
            )
        await ctx.reply(f'{case.client}\'s case is now {"Active" if case.active else "Inactive"}.')


@command("assign", "add", "go", require_channel=True, require_permission=RAT)
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
            rat = Rat(name=name.casefold(), uuid=None)
            await case.add_rat(rat)

            if rat.name in case.unidentified_rats and not ctx.DRILL_MODE:
                await ctx.reply(f"Warning: {name!r} is NOT identified.")

    await ctx.reply(
        f"{rescue_client}: Please add the following rat(s) to your friends list:"
        f' {", ".join(str(rat) for rat in rat_list)}'
    )


@command("clear", "close", require_permission=RAT, require_channel=True)
async def cmd_case_management_clear(ctx: Context):
    if not CLEAR_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !clear <Client Name|Board Index> [First Limpet Sender]")
        return
    tokens = CLEAR_PATTERN.parseString(ctx.words_eol[0])
    # Pass case to validator, return a case if found or None
    rescue = ctx.bot.board.get(tokens.subject[0])

    first_limpet = tokens.first_limpet[0].casefold() if tokens.first_limpet else None

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    if not rescue.system:
        return await ctx.reply("Cannot comply: system not set.")
    if not rescue.platform:
        return await ctx.reply("Cannot comply: platform not set.")
    if first_limpet:
        logger.debug("clearning rescue to FL {}", first_limpet)
        if first_limpet in rescue.unidentified_rats and not ctx.DRILL_MODE:
            return await ctx.reply(f"Cannot comply: {first_limpet!r}  is unidentified.")
        if first_limpet not in rescue.rats and first_limpet not in rescue.unidentified_rats:
            return await ctx.reply(f"Cannot comply: {first_limpet!r} is not assigned to this rescue")
    async with ctx.bot.board.modify_rescue(rescue) as case:
        case.active = False
        case.status = Status.CLOSED
        # If we are drill mode, just:tm: don't add the first limpet association
        # as we probably don't have valid user data in the drill API.
        if first_limpet and not ctx.DRILL_MODE:
            case.first_limpet = rescue.rats[first_limpet].uuid
            # TODO: Add paperwork call link here

    await ctx.bot.board.remove_rescue(rescue)

    await ctx.reply(f"Case {case.client} was cleared!")


@command("cmdr", "commander", require_channel=True, require_permission=RAT)
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


@command("codered", "casered", "cr", require_channel=True, require_permission=RAT)
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


@command("delete", require_channel=True, require_permission=OVERSEER)
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


@command("epic", require_channel=True, require_permission=RAT)
async def cmd_case_management_epic(ctx: Context):
    # This command may be depreciated, and not used.  It's left in only as an artifact, or
    # if that changes.
    await ctx.reply(
        "This command is no longer in use.  "
        "Please visit https://fuelrats.com/epic/nominate to nominate an epic rescue."
    )
    warnings.warn("call to deprecated command", DeprecationWarning)


@command("grab", require_channel=True, require_permission=RAT)
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
        return await ctx.reply(
            f"There is no open case for {tokens.subject[0]}. "
            f"Please first create one with '!inject {tokens.subject[0]} [CR] [PC/PS/XB]'"
        )

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


@command("inject", require_channel=True, require_permission=RAT)
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
    # build a list of possible words that was the subject
    possible_words = {word for word in ctx.words if word.startswith(f"{tokens.subject[0]}")}
    # and assert that at least one of these is equal to the subject.
    # to prevent daft input like `!inject sǝʌıɥↃ‾ǝıssn∀ Helgoland PC ok` from working.
    if not any(word == f"{tokens.subject[0]}" for word in possible_words):
        # if the subject doesn't match
        return await ctx.reply("Invalid IRC nick for inject. Abort.")

    if not rescue and not isinstance(tokens.subject[0], int):
        logger.debug("creating rescue for {!r}", tokens.subject[0])
        rescue = await ctx.bot.board.create_rescue(client=tokens.subject[0])
        async with ctx.bot.board.modify_rescue(rescue, impersonation=ctx.user.account) as case:
            case.add_quote(ctx.words_eol[0], ctx.user.nickname)

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
                f"{case.client}'s case opened with: " f"{ctx.words_eol[0]}  (Case {case.board_index})"
            )

            if case.code_red:
                await ctx.reply(f"Code Red! {case.client} is on Emergency Oxygen!")

            return

    if len(ctx.words_eol) < 3:
        return await ctx.reply("Cannot comply: no inject message.")

    async with ctx.bot.board.modify_rescue(rescue, impersonation=ctx.user.account) as case:
        case.add_quote(ctx.words_eol[0], ctx.user.nickname)

    await ctx.reply(
        f"{case.client}'s case updated with: {ctx.words_eol[2]!r} (Case {case.board_index})"
    )


@command("ircnick", "nick", "nickname", require_channel=True, require_permission=RAT)
async def cmd_case_management_ircnick(ctx: Context):
    if not IRC_NICK_PATTERN.matches(ctx.words_eol[0]):
        return await ctx.reply("Usage: !ircnick <Client Name|Board Index> <New Client Name>")
    tokens = IRC_NICK_PATTERN.parseString(ctx.words_eol[0])
    # Pass case to validator, return a case if found or None
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    new_name = tokens.new_nick[0]
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


@command("pc", "ps", "xb", require_channel=True, require_permission=RAT)
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


@command("quiet", require_channel=True, require_permission=RAT)
async def cmd_case_management_quiet(ctx: Context):
    # Check if there is an active rescue
    """
    if ctx.bot is not None:
        if ctx.bot.board is not None:
    """
    for rescue in ctx.bot.board.values():
        if rescue.active:
            await ctx.reply("There is corrently an active rescue")
            return

    if not ctx.bot.board.last_case_datetime:
        await ctx.reply("Got no information yet")
        return

    human_delta = pendulum.now().diff_for_humans(ctx.bot.board.last_case_datetime)
    if "before" in human_delta:
        logger.warning(
            "computed delta is in the future, this shouldn't be possible... {!r}", human_delta
        )
    await ctx.reply(f"The last case was created {human_delta.replace('after', 'ago')}.")


@command("quote", require_channel=True, require_permission=RAT)
async def cmd_case_management_quote(ctx: Context):
    if not JUST_RESCUE_PATTERN.matches(ctx.words_eol[0]):
        await ctx.reply("Usage: !quote <Client Name|Board Index>")
        return

    tokens = JUST_RESCUE_PATTERN.parseString(ctx.words_eol[0])
    rescue = ctx.bot.board.get(tokens.subject[0])

    if not rescue:
        await ctx.reply("No case with that name or number.")
        return

    template = template_environment.get_template("rescue.jinja2")
    flags = RescueRenderFlags(
        show_assigned_rats=True, show_unidentified_rats=True, show_quotes=True, show_uuids=True
    )
    output = await template.render_async(rescue=rescue, flags=flags)
    return await ctx.reply(output.rstrip("\n"))


@command("quoteid", require_channel=True, require_permission=OVERSEER)
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
                    (datetime.now() - quote.updated_at),
                    detailed=False,
                    max_units=2,
                )
                + " ago"
            )
            await ctx.reply(f"[{i}][{quote.author} ({quote_timestamp})] {quote.message}")


@command("sub", require_channel=True, require_permission=OVERSEER)
async def cmd_case_management_sub(ctx: Context):
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
            updated_at=pendulum.now(),
        )

        async with ctx.bot.board.modify_rescue(rescue) as case:
            case.quotes[quote_id] = new_quote
            await ctx.reply(f"Updated line {quote_id}.")
            return

    async with ctx.bot.board.modify_rescue(rescue) as case:
        del case.quotes[quote_id]
        await ctx.reply(f"Deleted line {quote_id}.")


@command("sys", "loc", "location", "system", require_channel=True, require_permission=RAT)
async def cmd_case_management_sys(ctx: Context):
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


@command("title", require_channel=True, require_permission=RAT)
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


@command("unassign", "rm", "remove", "standdown", require_channel=True, require_permission=RAT)
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

    flags = RescueRenderFlags()
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
                flags = RescueRenderFlags.from_word(word)
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

        output = await template_environment.get_template("list.jinja2").render_async(
            rescues=active_rescues, flags=flags
        )
        if output:
            await ctx.reply(output.rstrip("\n"))
    if flags.show_inactive:
        if not inactive_rescues:
            return await ctx.reply("No inactive rescues.")

        output = await template_environment.get_template("list.jinja2").render_async(
            rescues=inactive_rescues, flags=flags
        )
        if output:
            await ctx.reply(output.rstrip("\n"))


def _list_rescue(rescue_collection, format_specifiers):
    buffer = io.StringIO()
    buffer.write(f"{len(rescue_collection)} active cases. ")
    for rescue in rescue_collection:
        buffer.write(format(rescue, format_specifiers))
        buffer.write("\n")
    output = buffer.getvalue()
    return output.rstrip("\n")


def _rescue_filter(
    flags: RescueRenderFlags, platform_filter: typing.Optional[Platforms], rescue: Rescue
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


@command("reopen", require_channel=True, require_permission=OVERSEER)
async def cmd_reopen(context: Context):
    """ Re-open a closed rescue """
    if not REOPEN_PATTERN.matches(context.words_eol[0]):
        return await context.reply("usage: !reopen <API-ID>")

    tokens = REOPEN_PATTERN.parseString(context.words_eol[0])
    # contextualize subsequent logging calls with the API ID of the request
    with logger.contextualize(api_id=tokens.subject[0]):
        logger.debug("attempting to reopen rescue by UUID {}...", tokens.subject[0])

        rescue = await context.bot.board.api_handler.get_rescue(
            key=tokens.subject[0], impersonation=context.user.account
        )
        if not rescue:
            return await context.reply(f"no such rescue by id @{tokens.subject[0]}")

        # We have a rescue, check that the board id / ircnick isn't already in use.

        if rescue.irc_nickname in context.bot.board:
            return await context.reply(
                f"Cannot comply, {rescue.irc_nickname!r} currently has an open rescue."
            )

        if rescue.board_index in context.bot.board:
            logger.debug(
                "board index collision, reassigning re-opened case's index to avoid conflict."
            )
            rescue.board_index = context.bot.board.free_case_number
        logger.trace("appending reopened rescue to board")

        await context.bot.board.append(rescue)
        async with context.bot.board.modify_rescue(rescue) as rescue:
            rescue.status = Status.OPEN
            rescue.unmark_delete()

        return await context.reply(f"reopened {rescue.client}'s case #{rescue.board_index}.")
