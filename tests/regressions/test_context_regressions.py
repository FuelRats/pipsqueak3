"""
PyTest module for Context-specific regressions
"""

from pytest import mark

from Modules import rat_command, context
from Modules.rat_command import command, prefix


@mark.asyncio
@mark.regressions
async def test_on_command_double_prefix(bot_fx, monkeypatch, context_fx, async_callable_fx,
                                        user_fx):
    """
    Verifies that when commands are prefixed with the command prefix during registration,
    they remain invokable during runtime.
    """

    context.sender.set(user_fx.nickname)
    context.user.set(user_fx)
    context.prefixed.set(True)
    context.message = f"{prefix}{prefix}boom"
    context.words.set([f"{prefix}boom"])
    context.words_eol.set([f'{prefix}boom'])

    monkeypatch.setattr(rat_command, "_registered_commands", dict())

    @command(f"{prefix}boom")
    async def cmd_boom():
        return 42

    result = await rat_command.trigger()
    assert 42 == result
