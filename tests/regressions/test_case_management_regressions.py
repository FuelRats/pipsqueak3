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


async def test_spark_239(bot_fx, rescue_sop_fx, monkeypatch):
    await bot_fx.board.append(rescue_sop_fx)
    assign_payload = f"!assign {rescue_sop_fx.board_index} Unknown"
    context = await Context.from_message(bot=bot_fx, channel="#fuelrats", sender="some_ov",
                                         message=assign_payload)

    await trigger(context)
    assert "unknown" in rescue_sop_fx.unidentified_rats

    assign_payload = f"!clear {rescue_sop_fx.board_index} unknown"
    context = await Context.from_message(bot=bot_fx, channel="#fuelrats", sender="some_ov",
                                         message=assign_payload)
    # since this test is against an unidentified rat, this is only gunna work in drill mode.
    # drill mode can be faked by setting DRILL_MODE on context.
    monkeypatch.setattr(context, "DRILL_MODE", True)

    await trigger(context)

    assert rescue_sop_fx.client not in bot_fx.board


async def test_spark_242(bot_fx):
    """
    Verifies that `!inject {name}` returns an usage error instead of dying horribly.
    """

    pre_len = len(bot_fx.board)

    ctx = await Context.from_message(bot_fx, "#fuelrats", "Some_ov", "!inject sinkhole")

    await trigger(ctx=ctx)

    assert "sinkhole" in bot_fx.board
    assert len(bot_fx.board) == pre_len + 1

    # verify that a) the inject doesn't break things a second time and b) that a new rescue isn't
    # created when the inject is repeated.
    await trigger(ctx=ctx)
    assert len(bot_fx.board) == pre_len + 1, "That wasn't supposed to create *another* rescue."
