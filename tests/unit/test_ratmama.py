"""
test_ratmama.py - Tests for the Ratmama.py

Tests the parsing facilities for ratsignals

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import pytest

import src.packages.ratmama as ratmama
from src.packages.context.context import Context
from src.packages.rescue.rat_rescue import Platforms

pytestmark = [pytest.mark.unit, pytest.mark.ratsignal_parse, pytest.mark.asyncio]


@pytest.mark.parametrize("announcement, signal, cmdr, system, platform, code_red", [
    ("Incoming Client: SomeClient - System: Fuelum - Platform: PC - O2: OK"
     " - Language: English (en-US)",
     "DRILLSIGNAL - CMDR SomeClient - Reported System: Fuelum (distance to be implemented)"
     " - Platform: PC - O2: OK - Language: English (en-US) (Case #{}) (PC_SIGNAL)",
     "SomeClient", "FUELUM", Platforms.PC, False),
    ("Incoming Client: SomeOtherClient - System: LHS 3447 - Platform: XB"
     " - O2: NOT OK - Language: German (de-DE)",
     "DRILLSIGNAL - CMDR SomeOtherClient - Reported System: LHS 3447 (distance to be implemented)"
     " - Platform: XB - O2: NOT OK - Language: German (de-DE) (Case #{}) (XB_SIGNAL)",
     "SomeOtherClient", "LHS 3447", Platforms.XB, True),
    
    # These three tests specifically target an edge case where we accidentally create two cases
    # if there's a client named R@signal or Drillsignal
    ("Incoming Client: Ratsignal - System: LHS 3447 - Platform: XB"
     " - O2: OK - Language: English (en-US)",
     "DRILLSIGNAL - CMDR Ratsignal - Reported System: LHS 3447 (distance to be implemented)"
     " - Platform: XB - O2: OK - Language: English (en-US) (Case #{}) (XB_SIGNAL)",
     "Ratsignal", "LHS 3447", Platforms.XB, False),
    ("Incoming Client: Drillsignal - System: LHS 3447 - Platform: PS"
     " - O2: NOT OK - Language: English (en-US)",
     "DRILLSIGNAL - CMDR Drillsignal - Reported System: LHS 3447 (distance to be implemented)"
     " - Platform: PS - O2: NOT OK - Language: English (en-US) (Case #{}) (PS_SIGNAL)",
     "Drillsignal", "LHS 3447", Platforms.PS, True),

    # This is also an edge case, attempting to create a rescue for a service.
    ("Incoming Client: some_service - System: LHS 3447 - Platform: PS"
     " - O2: NOT OK - Language: English (en-US)",
     "DRILLSIGNAL - CMDR some_service - Reported System: LHS 3447 (distance to be implemented)"
     " - Platform: PS - O2: NOT OK - Language: English (en-US) (Case #{}) (PS_SIGNAL)",
     "some_service", "LHS 3447", Platforms.PS, True)
])
async def test_announcer_parse(bot_fx,
                               async_callable_fx,
                               monkeypatch,
                               announcement: str,
                               signal: str,
                               cmdr: str,
                               system: str,
                               platform: 'Platform',
                               code_red: bool):
    """
    Test that a received signal is parsed and a case is created as expected.
    """

    context = await Context.from_message(bot_fx, "#unit_test", "some_announcer", announcement)

    await ratmama.handle_ratmama_announcement(context)

    # Testing for the edge case referenced above.  We should not create a case
    # for the announcer, bot, or service account
    assert "some_announcer" not in context.bot.board
    assert "some_service" not in context.bot.board

    # We can't very well check for something we don't expect!
    if "some_service" != cmdr:
        rescue = context.bot.board[cmdr]
        assert rescue is not None
        assert rescue.client == cmdr
        assert rescue.system == system
        assert rescue.platform == platform
        assert rescue.code_red == code_red

        index = rescue.board_index
        signal = signal.format(str(index))
        message = bot_fx.sent_messages.pop(0)["message"]
        assert message.casefold() == signal.casefold()
    else:
        assert bot_fx.sent_messages.pop(0)["message"] == \
               "Signal attempted to create rescue for a service. Dispatch: please inject this case."


async def test_announcer_invalid_platform(bot_fx, async_callable_fx, monkeypatch):
    """
    Test that an announcement with an invalid platform doesn't ruin the rest of the case.
    """

    context = await Context.from_message(bot_fx,
                                         "#unit_test",
                                         "some_announcer",
                                         "Incoming Client: SomeClient - System: Fuelum"
                                         " - Platform: NES - O2: OK - Language: English (en-US)")
    monkeypatch.setattr(context, "reply", async_callable_fx)

    await ratmama.handle_ratmama_announcement(context)

    assert context.bot.board["SomeClient"] is not None


async def test_announcer_reconnect(bot_fx, async_callable_fx, monkeypatch):
    """
    Tests that a client reconnecting with an active case is announced as such.
    """

    context = await Context.from_message(bot_fx,
                                         "#unit_test",
                                         "some_announcer",
                                         "Incoming Client: SomeClient - System: Fuelum"
                                         " - Platform: PC - O2: OK - Language: English (en-US)")
    monkeypatch.setattr(context, "reply", async_callable_fx)

    await ratmama.handle_ratmama_announcement(context)
    await ratmama.handle_ratmama_announcement(context)

    rescue = context.bot.board["SomeClient"]
    index = rescue.board_index

    assert async_callable_fx.was_called_with(f"SomeClient has reconnected! Case #{index} (RETURN_SIGNAL)")


async def test_announcer_reconnect_with_changes(bot_fx, async_callable_fx, monkeypatch):
    """
    Tests that a client reconnecting with differing information from their existing case is
    reported as such.
    """

    context = await Context.from_message(bot_fx,
                                         "#unit_test",
                                         "some_announcer",
                                         "Incoming Client: SomeClient - System: Fuelum"
                                         " - Platform: PC - O2: OK - Language: English (en-US)")
    context2 = await Context.from_message(bot_fx,
                                          "#unit_test",
                                          "some_announcer",
                                          "Incoming Client: SomeClient - System: Sol - "
                                          "Platform: XB - O2: NOT OK - Language: English (en-US)")
    monkeypatch.setattr(context, "reply", async_callable_fx)
    monkeypatch.setattr(context2, "reply", async_callable_fx)

    await ratmama.handle_ratmama_announcement(context)
    await ratmama.handle_ratmama_announcement(context2)

    assert async_callable_fx.was_called_with('Case #0 system, platform, O2 Status changed, '
                                             'it is now CODE RED! O2 Status changed, it is now CODE RED!')


async def test_announce_from_invalid_user(bot_fx, async_callable_fx, monkeypatch):
    """
    Tests that a valid signal received from an invalid user does not trigger a case creation.
    """

    context = await Context.from_message(bot_fx,
                                         "#unit_test",
                                         "some_recruit",
                                         "Incoming Client: SomeClient - System: Fuelum"
                                         " - Platform: PC - O2: OK - Language: English (en-US)")
    monkeypatch.setattr(context, "reply", async_callable_fx)

    await ratmama.handle_ratmama_announcement(context)

    assert not async_callable_fx.was_called
    assert "SomeClient" not in context.bot.board



@pytest.mark.parametrize("signal, platform, system, code_red", [
    ("ratsignal pc, lhs 3447", Platforms.PC, "LHS 3447", False),
    ("RATSIGNAL xbox - o2 not ok", Platforms.XB, None, True),
    ("RatSignal o2 ok;ps4;sol", Platforms.PS, "SOL", False),
    ("RaTsIgNaL rODentIa    | Pc", Platforms.PC, "RODENTIA", False),
    ("ratsignal", None, None, False)
])
async def test_manual_signal(bot_fx,
                             async_callable_fx,
                             monkeypatch,
                             signal: str,
                             platform: 'Platform',
                             system: str,
                             code_red: bool):
    """
    Tests that a manual signal from a standard user is parsed and a case is created accordingly.
    """

    context = await Context.from_message(bot_fx,
                                         "#unit_test",
                                         "some_recruit",
                                         signal)
    monkeypatch.setattr(context, "reply", async_callable_fx)

    await ratmama.handle_ratsignal(context)

    rescue = context.bot.board["some_recruit"]
    assert rescue is not None
    assert rescue.client == "some_recruit"
    assert rescue.platform == platform
    assert rescue.system == system
    assert rescue.code_red == code_red


async def test_manual_signal_service_account(
        bot_fx,
        async_callable_fx,
        monkeypatch):

    context = await Context.from_message(
        bot_fx,
        "#unit_test",
        "unit_test",
        "Ratsignal some_service")

    await ratmama.handle_ratsignal(context)

    assert "some_service" not in context.bot.board


async def test_manual_signal_duplicate(bot_fx, async_callable_fx, monkeypatch):
    """
    Tests that a manual signal received for someone who has a case already is replied to as such.
    """

    context = await Context.from_message(bot_fx,
                                         "#unit_test",
                                         "some_recruit",
                                         "ratsignal Sol, PC, O2 OK")
    monkeypatch.setattr(context, "reply", async_callable_fx)

    await ratmama.handle_ratsignal(context)
    await ratmama.handle_ratsignal(context)

    assert async_callable_fx.was_called_with("some_recruit: You already sent a Signal! Please stand"
                                             " by, someone will help you soon!")
