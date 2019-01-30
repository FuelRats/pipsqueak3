"""

# TODO: 
"""

import pytest
from Modules.rat_board import RatBoard
from tests.mock_callables import AsyncCallableMock
from Modules.context import Context
import Modules.RatMama as RatMama
from Modules.rat_rescue import Platforms
from Modules.rat_rescue import Rescue

pytestmark = [pytest.mark.ratmama, pytest.mark.asyncio]


class test_ratsignal:
    rat_board: RatBoard

    def __init__(self, rat_board_fx):
        self.rat_board = rat_board_fx

    async def test_ratmama_arrival_and_rearrival(self, rat_board_fx: RatBoard,
                                                 async_callable_fx: AsyncCallableMock,
                                                 context_channel_fx: Context,
                                                 monkeypatch
                                                 ):
        """
        Tests the RSignal announcement as well as the reconnect message.
        """
        monkeypatch.setattr(context_channel_fx, 'reply', async_callable_fx)
        RatMama.board = rat_board_fx

        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: Alrai - "
                             "Platform: PC - O2: OK - Language: Polish (pl-PL)"
                             ]
                            )

        monkeypatch.setattr(context_channel_fx._user, '_nickname', "RatMama[BOT]")
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        rescue: Rescue = RatMama.board.find_by_name("Ajdacho")
        index = rescue.board_index
        assert async_callable_fx.was_called_with(
            f"RATSIGNAL - CMDR Ajdacho - "
            f"Reported System: Alrai (distance to be implemented) - "
            f"Platform: PC - "
            f"O2: OK - "
            f"Language: Polish (pl-PL) (Case #{index}) (PC_SIGNAL)")

        async_callable_fx.reset()

        await RatMama.handle_ratmama_announcement(context_channel_fx)
        assert async_callable_fx.was_called_with(
            f"Ajdacho has reconnected! Case #{index}"
        )

    async def test_reconnect_with_changes(self, rat_board_fx: RatBoard,
                                          async_callable_fx: AsyncCallableMock,
                                          context_channel_fx: Context,
                                          monkeypatch
                                          ):
        """
        Tests the recognition of changes and the emission of the associated message.
        Tests a single case only
        """
        monkeypatch.setattr(context_channel_fx, 'reply', async_callable_fx)
        RatMama.board = rat_board_fx

        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: Alrai - "
                             "Platform: PC - O2: OK - Language: Polish (pl-PL)"
                             ]
                            )

        monkeypatch.setattr(context_channel_fx._user, '_nickname', "RatMama[BOT]")
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        index = RatMama.board.find_by_name("Ajdacho").board_index

        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: H - Platform: XB - "
                             "O2: OK - Language: Polish (pl-PL)"
                             ]
                            )

        async_callable_fx.reset()
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        assert async_callable_fx.was_called_with(
            f"Ajdacho has reconnected! Case #{index}"
        )

        assert async_callable_fx.was_called_with(
            "System changed! Platform changed! "
        )
        async_callable_fx.reset()
        monkeypatch.setattr(context_channel_fx._user, '_nickname', "MasterLoon")
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        assert not async_callable_fx.was_called

    async def test_no_action_on_wrong_nick(self, async_callable_fx: AsyncCallableMock,
                                           context_channel_fx: Context,
                                           monkeypatch):
        """
        Tests, that a wrong nickname has no associated action when handed to the RatMama handler.
        """
        async_callable_fx.reset()
        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: H - Platform: XB - "
                             "O2: OK - Language: Polish (pl-PL)"
                             ]
                            )

        monkeypatch.setattr(context_channel_fx._user, '_nickname', "MasterLoon")
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        assert not async_callable_fx.was_called

    async def test_manual_rsig_handler(self, rat_board_fx: RatBoard,
                                       async_callable_fx: AsyncCallableMock,
                                       context_channel_fx: Context,
                                       monkeypatch):
        """
        Tests with multiple cases, that the parser recognized the case details
        and creates an appropriate rescue
        """

        monkeypatch.setattr(context_channel_fx, 'reply', async_callable_fx)
        RatMama.board = rat_board_fx

        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["ratsignal H, XB, O2 OK"]
                            )

        monkeypatch.setattr(context_channel_fx._user, '_nickname', "Absolver")
        await RatMama.handle_selfissued_ratsignal(context_channel_fx)
        case = rat_board_fx.find_by_name("Absolver")

        assert case is not None
        assert case.platform == Platforms.XB
        assert case.system.casefold() == "h"
        assert case.irc_nickname.casefold() == "absolver"
        assert not case.code_red

        rat_board_fx.clear_board()

        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["ratsignal H; XB; O2 OK"]
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
                            ["ratsignalCol 285| Ps| O2 NOT OK"]
                            )

        monkeypatch.setattr(context_channel_fx._user, '_nickname', "Absolver")
        await RatMama.handle_selfissued_ratsignal(context_channel_fx)
        case = rat_board_fx.find_by_name("Absolver")

        assert case is not None
        assert case.platform == Platforms.PS
        assert case.system.casefold() == "col 285"
        assert case.irc_nickname.casefold() == "absolver"
        assert case.code_red
