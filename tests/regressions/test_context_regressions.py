"""
PyTest module for Context-specific regressions
"""

from pytest import mark

from Modules.context import Context


@mark.asyncio
@mark.regressions
async def test_on_command_double_prefix(bot_fx, monkeypatch, context_fx, callable_fx,
                                        command_registry_fx):
    """
    Verifies that when commands are prefixed with the command prefix during registration,
    they remain invokable during runtime.
    """

    ctx = await Context.from_message(bot_fx, "#unit_test", context_fx.user.nickname,

                                     f"{bot_fx.prefix}{bot_fx.prefix}boom")

    @command_registry_fx.register(f"{bot_fx.prefix}boom")
    async def cmd_boom(context: Context):
        callable_fx()

    await command_registry_fx[f"{bot_fx.prefix}boom"](ctx)

    assert callable_fx.was_called
    assert callable_fx.was_called_once
