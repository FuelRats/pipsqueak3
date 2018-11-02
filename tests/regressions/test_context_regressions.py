"""
PyTest module for Context-specific regressions
"""

from pytest import mark

from Modules import rat_command
from Modules.context import Context
from Modules.rat_command import command, prefix
from Modules.user import User


@mark.asyncio
@mark.regressions
async def test_on_command_double_prefix(bot_fx, monkeypatch, context_fx, async_callable_fx):
    """
    Verifies that when commands are prefixed with the command prefix during registration,
    they remain invokable during runtime.
    """
    async_callable_fx.return_value = context_fx.user

    # patch the whois lookup as its outside the scope of our test.
    monkeypatch.setattr(User, "from_pydle", async_callable_fx)

    ctx = await Context.from_message(bot_fx, "#unit_test", context_fx.user.nickname,

                                     f"{prefix}{prefix}boom")

    monkeypatch.setattr(rat_command, "_registered_commands", dict())

    @command(f"{prefix}boom")
    async def cmd_boom(context: Context):
        return 42

    result = await rat_command.trigger(ctx=ctx)
    assert 42 == result
