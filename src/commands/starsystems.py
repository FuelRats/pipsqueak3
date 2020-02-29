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
