import pytest

from src.packages.commands import trigger
from src.packages.context import Context

pytestmark = [pytest.mark.regressions, pytest.mark.asyncio]


async def test_spark_214(bot_fx):
    context = await Context.from_message(bot=bot_fx, channel="#ratchat", sender="some_ov",
                                         message="!inject foo PC")
    await trigger(ctx=context)

    _rescue = bot_fx.board['foo']

    pre_state = _rescue.code_red

    context = await Context.from_message(bot=bot_fx, channel="#ratchat", sender="some_ov",
                                         message="!cr 0")
    await trigger(ctx=context)

    assert _rescue.code_red != pre_state, "!cr failed to flip CR state"


async def test_spark_223_command(bot_fx):
    pre_len = len(bot_fx.board)
    context = await Context.from_message(bot=bot_fx, channel="#ratchat", sender="some_ov",
                                         message="!inject sǝʌıɥↃ‾ǝıssn∀ Helgoland PC ok")
    await trigger(ctx=context)

    assert len(bot_fx.board) == pre_len, "number of rescues changed unexpectedly!"
