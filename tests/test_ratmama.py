"""

TEST will be added laters
"""

import pytest
from Modules.rat_board import RatBoard
from tests.mock_callables import AsyncCallableMock
from Modules.context import Context
import Modules.RatMama as RatMama
from tests.mock_callables import InstanceOf
from Modules.rat_rescue import Platforms

pytestmark = pytest.mark.ratmama


@pytest.mark.asyncio
async def test_ratmama_announcement(rat_board_fx: RatBoard, async_callable_fx: AsyncCallableMock,
                                    context_channel_fx: Context, monkeypatch):
    async def f(msg: str):
        print(f"would have replied with: {msg}")
        await async_callable_fx(msg)

    monkeypatch.setattr(context_channel_fx, 'reply', f)
    RatMama.board = rat_board_fx

    monkeypatch.setattr(context_channel_fx, '_words_eol',
                        ["Incoming Client: Ajdacho - System: Alrai - "
                         "Platform: PC - O2: OK - Language: Polish (pl-PL)"
                         ]
                        )

    monkeypatch.setattr(context_channel_fx._user, '_nickname', "RatMama[BOT]")
    await RatMama.handle_ratmama_announcement(context_channel_fx)
    index = RatMama.board.find_by_name("Ajdacho").board_index
    # assert async_callable_fx.was_called_with(
    #     f"RATSIGNAL - CMDR Ajdacho - "
    #     f"Reported System: Alrai (distance to be implemented) - "
    #     f"Platform: PC - "
    #     f"O2: OK - "
    #     f"Language: Polish (pl-PL) (Case #{index}) (PC_SIGNAL)")

    assert async_callable_fx.was_called_with(InstanceOf(str))

    async_callable_fx.reset()

    await RatMama.handle_ratmama_announcement(context_channel_fx)
    assert async_callable_fx.was_called_with(
        InstanceOf(str)
    )
    assert async_callable_fx.was_called_once

    monkeypatch.setattr(context_channel_fx, '_words_eol',
                        ["Incoming Client: Ajdacho - System: H - Platform: XB - "
                         "O2: OK - Language: Polish (pl-PL)"]
                        )

    async_callable_fx.reset()
    await RatMama.handle_ratmama_announcement(context_channel_fx)
    assert async_callable_fx.was_called_with(
        InstanceOf(str)
    )

    assert async_callable_fx.was_called_with(
        InstanceOf(str)
    )

    assert len(async_callable_fx.calls) == 2

    async_callable_fx.reset()
    monkeypatch.setattr(context_channel_fx._user, '_nickname', "MasterLoon")
    await RatMama.handle_ratmama_announcement(context_channel_fx)
    assert not async_callable_fx.was_called


@pytest.mark.asyncio
async def test_manual_rsig_handler(rat_board_fx: RatBoard, async_callable_fx: AsyncCallableMock,
                                   context_channel_fx: Context, monkeypatch):
    async def f(msg: str):
        print(f"would have replied with: {msg}")
        await async_callable_fx(msg)

    monkeypatch.setattr(context_channel_fx, 'reply', f)
    RatMama.board = rat_board_fx
    monkeypatch.setattr(context_channel_fx, '_words_eol',
                        ["ratsignal H, XB, O2 OK"
                         ]
                        )
    monkeypatch.setattr(context_channel_fx._user, '_nickname', "Absolver")
    await RatMama.handle_selfissued_ratsignal(context_channel_fx)
    case = rat_board_fx.find_by_name("Absolver")
    assert (
        case is not None and
        case.platform == Platforms.XB and
        case.system.casefold() == "h" and
        case.irc_nickname.casefold() == "absolver" and
        not case.code_red
    )
    rat_board_fx.clear_board()

    monkeypatch.setattr(context_channel_fx, '_words_eol',
                        ["ratsignal H; XB; O2 OK"
                         ]
                        )
    monkeypatch.setattr(context_channel_fx._user, '_nickname', "Absolver")
    await RatMama.handle_selfissued_ratsignal(context_channel_fx)
    case = rat_board_fx.find_by_name("Absolver")
    assert (
            case is not None and
            case.platform == Platforms.XB and
            case.system.casefold() == "h" and
            case.irc_nickname.casefold() == "absolver" and
            not case.code_red
    )
    rat_board_fx.clear_board()

    monkeypatch.setattr(context_channel_fx, '_words_eol',
                        ["ratsignalCol 285| PS| O2 NOT OK"
                         ]
                        )
    monkeypatch.setattr(context_channel_fx._user, '_nickname', "Absolver")
    await RatMama.handle_selfissued_ratsignal(context_channel_fx)
    case = rat_board_fx.find_by_name("Absolver")
    assert (
            case is not None and
            case.platform == Platforms.PS and
            case.system.casefold() == "col 285" and
            case.irc_nickname.casefold() == "absolver" and
            case.code_red
    )
    rat_board_fx.clear_board()
