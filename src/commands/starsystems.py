from ..packages.context import Context
from ..packages.commands import command
from ..packages import permissions
import pyparsing
from loguru import logger


@permissions.require_permission(permissions.RAT)
@command("search")
async def cmd_search(ctx: Context):
    if len(ctx.words) != 2:
        return await ctx.reply("Usage: search <name of system>")
    results = await ctx.bot.galaxy.search_systems_by_name(ctx.words[1])
    return await ctx.reply(f"{results!r}")


async def cmd_landmark_near(ctx: Context, system_name: str):
    logger.trace("searching for system {}", system_name)
    found = await ctx.bot.galaxy.find_system_by_name(system_name)
    if not found:
        return await ctx.reply(f"{system_name} was not found in The Fuel Rats System Database.")

    logger.debug("found system {}, acquiring nearest landmark...", found)
    nearest_landmark, distance = await ctx.bot.galaxy.find_nearest_landmark(found)
    return await ctx.reply(f"{found.name} is {distance:.2f} LY from {nearest_landmark.name}")


@permissions.require_permission([permissions.RAT])
@command("landmark")
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
