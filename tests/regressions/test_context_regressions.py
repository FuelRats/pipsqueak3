"""
PyTest module for Context-specific regressions
"""
import pyparsing
import pytest
from pytest import mark

from src.commands.case_management import ASSIGN_PATTERN
from src.packages.commands import rat_command
from src.packages.context.context import Context
from src.packages.commands import command
from src.packages.user.user import User
from loguru import logger
pytestmark = [mark.regressions, mark.asyncio]


async def test_on_command_double_prefix(bot_fx, monkeypatch, context_fx, async_callable_fx):
    """
    Verifies that when commands are prefixed with the command prefix during registration,
    they remain invokable during runtime.
    """
    async_callable_fx.return_value = context_fx.user

    # patch the whois lookup as its outside the scope of our test.
    monkeypatch.setattr(User, "from_pydle", async_callable_fx)

    ctx = await Context.from_message(bot_fx, "#unit_test", context_fx.user.nickname,

                                     f"{Context.PREFIX}{Context.PREFIX}boom")

    monkeypatch.setattr(rat_command, "_registered_commands", dict())

    @command(f"{Context.PREFIX}boom")
    async def cmd_boom(context: Context):
        return 42

    result = await rat_command.trigger(ctx=ctx)
    assert 42 == result


def test_spark_something():
    with pytest.raises(pyparsing.ParseException):
        ASSIGN_PATTERN.parseString("!go 0Test rik07")

