"""
test_ratmama.py - Tests for the Ratmama.py

Tests the parsing facilities for ratsignals

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import pytest
from Modules.rat_board import RatBoard
from tests.mock_callables import AsyncCallableMock
from Modules.context import Context
import Modules.RatMama as RatMama
from Modules.rat_rescue import Platforms
from Modules.rat_rescue import Rescue

pytestmark = [pytest.mark.ratmama, pytest.mark.asyncio]


class TestRSignal(object):
    rat_board: RatBoard

    async def test_ratmama_wrong_platform(self, context_channel_fx: Context,
                                                 monkeypatch
                                          ):
        """
        Tests, that the parser does not implode upon being given a wrong platform by RatMama
        """
        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: Alrai - "
                             "Platform: Switch - O2: OK - Language: Polish (pl-PL)"
                             ]
                            )

        # now we just set the nickname to the allowed on
        monkeypatch.setattr(context_channel_fx._user, '_nickname', "RatMama[BOT]")
        # and fire away!
        await RatMama.handle_ratmama_announcement(context_channel_fx)

    async def test_ratmama_arrival_and_rearrival(self, rat_board_fx: RatBoard,
                                                 async_callable_fx: AsyncCallableMock,
                                                 context_channel_fx: Context,
                                                 monkeypatch
                                                 ):
        """
        Tests the RSignal announcement as well as the reconnect message.
        """
        # use our own function for reply so we can track it's calls
        monkeypatch.setattr(context_channel_fx, 'reply', async_callable_fx)
        # and give it our own board, again, for tracking purposes
        RatMama.board = rat_board_fx

        # set the message to a valid announcement
        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: Alrai - "
                             "Platform: PC - O2: OK - Language: Polish (pl-PL)"
                             ]
                            )

        # now we just set the nickname to the allowed on
        monkeypatch.setattr(context_channel_fx._user, '_nickname', "RatMama[BOT]")
        # and fire away!
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        # lets grab the result!
        rescue: Rescue = rat_board_fx.find_by_name("Ajdacho")
        # remember the index
        index = rescue.board_index
        # and assert, the right announcement was to be send
        assert async_callable_fx.was_called_with(
            f"RATSIGNAL - CMDR Ajdacho - "
            f"Reported System: Alrai (distance to be implemented) - "
            f"Platform: PC - "
            f"O2: OK - "
            f"Language: Polish (pl-PL) (Case #{index}) (PC_SIGNAL)")

        # assert rescue details are as expected
        assert rescue.client.casefold() == "ajdacho"
        assert rescue.system.casefold() == "alrai"
        assert rescue.platform == Platforms.PC
        assert not rescue.code_red
        assert rescue.lang_id.casefold() == "pl"

        # fire it again
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        # and assure it recognized it as a reconnect
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
        # set up all our tracking
        monkeypatch.setattr(context_channel_fx, 'reply', async_callable_fx)
        RatMama.board = rat_board_fx

        # set our first message
        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: Alrai - "
                             "Platform: PC - O2: OK - Language: Polish (pl-PL)"
                             ]
                            )

        # set the nickname of the announcer
        monkeypatch.setattr(context_channel_fx._user, '_nickname', "RatMama[BOT]")
        # and have it processed
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        # remember the index (is important later!)
        index = rat_board_fx.find_by_name("Ajdacho").board_index

        # prepare second announcement, this one has different details,
        # but is from the same commander
        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: H - Platform: XB - "
                             "O2: NOT OK - Language: Polish (pl-PL)"
                             ]
                            )

        # and handle it
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        # make sure it recognized it as a reconnect
        assert async_callable_fx.was_called_with(
            f"Ajdacho has reconnected! Case #{index}"
        )

        # as well as the fact some stuff changes
        assert async_callable_fx.was_called_with(
            "System changed! Platform changed! O2 Status changed, it is now CODE RED!"
        )

    async def test_no_action_on_wrong_nick(self, async_callable_fx: AsyncCallableMock,
                                           context_channel_fx: Context,
                                           monkeypatch):
        """
        Tests, that a wrong nickname has no associated action when handed to the RatMama handler.
        """
        # use a valid announcement
        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            ["Incoming Client: Ajdacho - System: H - Platform: XB - "
                             "O2: OK - Language: Polish (pl-PL)"
                             ]
                            )

        # with an invalid nickname
        monkeypatch.setattr(context_channel_fx._user, '_nickname', "MasterLoon")
        # have it licked by the handler
        await RatMama.handle_ratmama_announcement(context_channel_fx)
        # make sure it tasted awful
        assert not async_callable_fx.was_called

    @pytest.mark.parametrize("sep", [',', ';', '|', '-'])
    @pytest.mark.parametrize("platform_str, platform",
                             [("pc", Platforms.PC), ("ps", Platforms.PS), ("ps4", Platforms.PS),
                              ("playstation", Platforms.PS), ("playstation4", Platforms.PS),
                              ("Playstation 4", Platforms.PS), ("xb", Platforms.XB),
                              ("xb1", Platforms.XB), ("xbox", Platforms.XB),
                              ("xbox one", Platforms.XB)
                              ]
                             )
    async def test_manual_rsig_handler(self, rat_board_fx: RatBoard,
                                       async_callable_fx: AsyncCallableMock,
                                       context_channel_fx: Context,
                                       monkeypatch,
                                       sep: chr,
                                       platform_str: str,
                                       platform: Platforms
                                       ):
        """
        Tests with multiple cases, that the parser recognized the case details
        and creates an appropriate rescue
        """

        # again, tracking stuff needs to be set up
        monkeypatch.setattr(context_channel_fx, 'reply', async_callable_fx)
        RatMama.board = rat_board_fx

        # give us a message
        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            [f"ratsignal H{sep} {platform_str}{sep} O2 OK"]
                            )

        # and a nickname
        monkeypatch.setattr(context_channel_fx._user, '_nickname', "Absolver")
        # throw it into the magic black box
        await RatMama.handle_selfissued_ratsignal(context_channel_fx)
        # and remember the result
        case = rat_board_fx.find_by_name("Absolver")

        # assert all details are as expected
        assert case is not None
        assert case.platform == platform
        assert case.system.casefold() == "h"
        assert case.irc_nickname.casefold() == "absolver"
        assert not case.code_red

        # who needs flash when they can have cleanse?
        rat_board_fx.clear_board()

        # now lets get a bit more mean with the message
        monkeypatch.setattr(context_channel_fx, '_words_eol',
                            [f"Ratsignal RaTsIgNaL{sep} RATSIGNAL ratsIGnalCol 285{sep} "
                             f"{platform_str}ratsignal{sep} o2 Not Ok please help! Ratsignal!"]
                            )

        # ensure who is the case summoner
        monkeypatch.setattr(context_channel_fx._user, '_nickname', "Absolver")
        # throw it into the abyss
        await RatMama.handle_selfissued_ratsignal(context_channel_fx)
        # catch the soul
        case = rat_board_fx.find_by_name("Absolver")

        # make sure we threw the right person into the abyss earlier
        assert case is not None
        assert case.platform == platform
        assert case.system.casefold() == "col 285"
        assert case.irc_nickname.casefold() == "absolver"
        assert case.code_red

    # @pytest.mark.xfail(reason="Rescue constructor is broken, making this break too")
    async def test_you_already_sent(self, async_callable_fx: AsyncCallableMock,
                                       context_channel_fx: Context,
                                       monkeypatch
                                    ):
        """
        Tests, that upon sending a ratsignal, the client will be nicely told that they already
        sent a signal
        """
        monkeypatch.setattr(context_channel_fx, 'reply', async_callable_fx)
        monkeypatch.setattr(context_channel_fx, '_words_eol', ["ratsignal"])
        monkeypatch.setattr(context_channel_fx.user, '_nickname', "po-ta-to")
        await RatMama.handle_selfissued_ratsignal(context_channel_fx)
        await RatMama.handle_selfissued_ratsignal(context_channel_fx)
        assert async_callable_fx.was_called_with(
            "You already sent a signal, please be patient while a dispatch is underway."
        )
