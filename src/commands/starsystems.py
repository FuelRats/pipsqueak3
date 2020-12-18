import asyncio

from ..packages.context import Context
from ..packages.commands import command
from ..packages import permissions
import pyparsing
from loguru import logger

from ..packages.parsing_rules import suppress_first_word

SEARCH_PATTERN = suppress_first_word + pyparsing.restOfLine.setResultsName("remainder")


@command("search", require_permission=permissions.RAT)
async def cmd_search(ctx: Context):
    if not SEARCH_PATTERN.matches(ctx.words_eol[0]):
        return await ctx.reply("Usage: search <name of system>")
    tokens = SEARCH_PATTERN.parseString(ctx.words_eol[0])
    try:
        results = await ctx.bot.galaxy.search_systems_by_name(tokens.remainder.strip())
    except asyncio.TimeoutError:
        return await ctx.reply(f"Been searching for {tokens.remainder.strip()!r} for too long... "
                               f"Giving up.")
    return await ctx.reply(f"{results!r}")


async def cmd_landmark_near(ctx: Context, system_name: str):
    logger.trace("searching for system {}", system_name)
    found = await ctx.bot.galaxy.find_system_by_name(system_name)
    if not found:
        return await ctx.reply(f"{system_name} was not found in The Fuel Rats System Database.")

    logger.debug("found system {}, acquiring nearest landmark...", found)
    nearest_landmark, distance = await ctx.bot.galaxy.find_nearest_landmark(found)
    return await ctx.reply(f"{found.name} is {distance:.2f} LY from {nearest_landmark.name}")


@command("landmark", require_permission=permissions.RAT)
@logger.catch(level="DEBUG")
async def cmd_landmark(ctx: Context):
    keyword = pyparsing.oneOf("near", asKeyword=True).setResultsName("subcommand")
    remainder = pyparsing.Word(pyparsing.alphanums + "- ").setResultsName("system")

    pattern = pyparsing.Suppress("landmark") + keyword + remainder
    try:
        logger.debug("attempting to parse landmark query {!r}", ctx.words_eol[0])
        result = pattern.parseString(ctx.words_eol[0].casefold())
    except pyparsing.ParseException:
        logger.exception("failed parse", level="DEBUG")
        return await ctx.reply("Usage: `landmark near <system>")
    logger.debug("successfully parsed landmark query, result {!r}", result)
    return await cmd_landmark_near(ctx, result.system)
