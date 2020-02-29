from ..packages.context import Context
from ..packages.commands import command
from ..packages import permissions


@permissions.require_permission(permissions.RAT)
@command("search")
async def cmd_search(ctx: Context):
    if len(ctx.words) != 2:
        return await ctx.reply("Usage: search <name of system>")
    results = await ctx.bot.galaxy.search_systems_by_name(ctx.words[1])
    return await ctx.reply(f"{results!r}")


@permissions.require_permission([permissions.RAT])
@command("landmark-near")
async def cmd_landmark_near(ctx: Context):
    if len(ctx.words) != 2:
        return await ctx.reply("Usage: landmark near <system>")

    found = await ctx.bot.galaxy.find_system_by_name(ctx.words[1].upper())
    if not found:
        return await ctx.reply(f"{ctx.words[1]} was not found in The Fuel Rats System Database.")
    return await ctx.bot.galaxy.find_nearest_landmark(found)
