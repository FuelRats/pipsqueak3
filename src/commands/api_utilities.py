"""
Utility commands involving the fuelrats API
"""
from src.packages.commands import command
from src.packages.context import Context
from src.packages.permissions import require_permission, RAT

from ..packages.parsing_rules import (
    rescue_identifier,
    irc_name,
    suppress_first_word,
    timer,
    rest_of_line,
    platform,
    api_id,
)

RATID_PATTERN = suppress_first_word + irc_name.setResultsName("subject")


@command("ratid", require_permission=RAT)
async def cmd_ratid(context: Context):
    if not RATID_PATTERN.matches(context.words_eol[0]):
        return await context.reply("Usage: !ratid <irc_nickname>")
    tokens = RATID_PATTERN.parseString(context.words_eol[0])

    results = await context.bot.api_handler.get_rat(
        key=tokens.subject[0], impersonation=context.user.account
    )

    if not results:
        return await context.reply(f"no rats found for {tokens.subject[0]!r}.")

    return await context.reply(
        ", ".join(f"{rat.name} on {rat.platform.colorize()}" for rat in results)
    )
