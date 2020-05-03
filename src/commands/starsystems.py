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


async def cmd_landmark_near(ctx: Context):
    if len(ctx.words) < 2:
        return await ctx.reply("Usage: landmark near <system>")

    system_name = ctx.words_eol[1]
    logger.trace("searching for system {}", system_name)
    found = await ctx.bot.galaxy.find_system_by_name(system_name)
    if not found:
        return await ctx.reply(
            f"{system_name} was not found in The Fuel Rats System Database.")

    logger.debug("found system {}, acquiring nearest landmark...", found)
    nearest_landmark = await ctx.bot.galaxy.find_nearest_landmark(found)
    return await ctx.reply(f"{nearest_landmark}")


@permissions.require_permission([permissions.RAT])
@command("landmark")
async def cmd_landmark(ctx: Context):
    keyword = pyparsing.oneOf("near", asKeyword=True).setResultsName(
        "subcommand")
    remainder = pyparsing.Word(pyparsing.alphanums + '- ').setResultsName(
        "system")

    pattern = pyparsing.Suppress(ctx.PREFIX) + pyparsing.Suppress(
        "landmark") + keyword + remainder
    if len(ctx.words) < 2:
        return await ctx.reply("Valid subcommands: 'near'")
