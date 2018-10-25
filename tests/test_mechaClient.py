"""
test_mechaClient.py - tests for the MechaClient
Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from typing import TYPE_CHECKING, List

from pytest import mark, raises

from Modules import events
from Modules.context import Context
from Modules.user import User
from config import config
from tests.mock_callables import InstanceOf, AsyncCallableMock

if TYPE_CHECKING:
    from Modules.events import Event

pytestmark = mark.mecha


@mark.asyncio
async def test_on_message(async_callable_fx, bot_fx):
    events.on_message.subscribe(async_callable_fx)

    await bot_fx.on_message("#unit_test", "unit_test", "hi there!")

    assert async_callable_fx.was_called


@mark.asyncio
async def test_on_channel_message(async_callable_fx, bot_fx):
    events.on_channel_message.subscribe(async_callable_fx)

    channel = "#unit_test"
    nickname = "unit_test"
    message = "hi there!"

    # make our clal
    await bot_fx.on_channel_message(channel, nickname, message)

    # assert the function was called with the expected argument
    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_with(context=InstanceOf(Context))

    # extract the received context from the call, as type hinting fails us here
    ctx: Context = async_callable_fx.calls[0].kwargs['context']

    # assert validity of the context
    assert ctx.target == channel
    assert ctx.words_eol[0] == message
    assert ctx.user.nickname == nickname


@mark.asyncio
async def test_on_invite(async_callable_fx, bot_fx):
    events.on_invite.subscribe(async_callable_fx)

    channel = "#invite_test"
    sender = "unit_test"
    await bot_fx.on_invite(channel, sender)

    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(channel=channel, sender=sender, bot=bot_fx)


@mark.asyncio
async def test_on_kick(async_callable_fx, bot_fx):
    events.on_kick.subscribe(async_callable_fx)
    kwargs = {
        "channel": "Hotseat",
        "target": "iceBox66",
        "sender": "Hotstix44",
        "reason": "too cool for skool",
    }

    await bot_fx.on_kick(**kwargs)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(**kwargs, bot=bot_fx)


@mark.asyncio
async def test_on_kill(async_callable_fx, bot_fx):
    events.on_kill.subscribe(async_callable_fx)
    kwargs = {
        "target": "#Hotstix44",
        "by": "WhiteSheets",
        "reason": "Get out."

    }
    await bot_fx.on_kill(**kwargs)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(**kwargs, bot=bot_fx)


@mark.asyncio
async def test_on_mode_change(async_callable_fx, bot_fx, user_fx):
    events.on_mode_change.subscribe(async_callable_fx)

    kwargs = {
        "channel": "#unit_test",
        "modes": ["-c", ""],
        "by": user_fx.nickname
    }
    await bot_fx.on_mode_change(**kwargs)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(**kwargs, bot=bot_fx)


@mark.asyncio
async def test_on_message_self(bot_fx, async_callable_fx):
    """
    Verifies what happens when :class:MechaClient gets a message from itself
    """
    # hook in a subscriber to on message
    events.on_message.subscribe(async_callable_fx)
    # lets also hook it into on_command, just to be sure
    events.on_command.subscribe(async_callable_fx)

    # call the method
    retn = await bot_fx.on_message("#unit_test", bot_fx.nickname, "potato")

    # ensure the callable didn't get called anyways
    assert not async_callable_fx.was_called

    # ensure we got the expected return type
    assert retn is None


@mark.asyncio
async def test_on_message_prefixed(bot_fx, async_callable_fx, monkeypatch):
    """
    Verifies that the command processor gets invoked when a prefixed
    message is received
    """
    # patch the event, so the existing hooks don't fire
    # the existing hooks (eg trigger) are outside the scope
    # of this test, and are not being tested here.
    monkeypatch.setattr(events.on_command, "subscribers", [])

    # mimic expected return
    async_callable_fx.return_value = NotImplemented

    # hook into the event
    events.on_command.subscribe(async_callable_fx)

    result = await bot_fx.on_message("#unit_test", "some_ov", "!trigger!!")

    assert async_callable_fx.was_called

    assert async_callable_fx.calls[0].kwargs['context'].prefixed

    assert [NotImplemented] == result


@mark.asyncio
async def test_on_message_plain(bot_fx, async_callable_fx, monkeypatch):
    """
    Verify the behavior when a non-prefixed message is received
    """
    # patch the event, so the existing hooks don't fire
    # any existing hooks are outside the scope
    # of this test, and are not being tested here.

    monkeypatch.setattr(events.on_message, "subscribers", [])

    # mimic expected return
    async_callable_fx.return_value = NotImplemented

    # hook into the event
    events.on_message.subscribe(async_callable_fx)

    await bot_fx.on_message("#unit_test", "some_recruit", "I like trains.💥🚅")

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(context=InstanceOf(Context))


@mark.asyncio
async def test_on_message_error_raised_graceful(bot_fx,

                                                monkeypatch):
    """
    Verifies that exceptions raised during message handling are
    gracefully handled (when they should be)
    """
    patch_events: List[Event] = [
        events.on_message,
        events.on_command,
        events.on_message_raw
    ]

    # patch out existing subscribers, they are irrelevant
    for event in patch_events:
        monkeypatch.setattr(event, "subscribers", [])

    # the bot fixture defaults to False here, but we want to test the default behavior (True)...
    monkeypatch.setattr(bot_fx, "graceful_errors", True)

    @events.on_message.subscribe
    async def boomstick(*args, **kwargs):
        """ goes boom"""
        raise RuntimeError

    result = await bot_fx.on_message("#unit_testing", "some_recruit", "💥stick")

    # the exception handling returns None...
    assert result is None


@mark.asyncio
async def test_on_message_error_raised_non_graceful(bot_fx,
                                                    monkeypatch):
    """
    Verifies that exceptions raised during message handling are
    not gracefully handled (when they should'nt be)

    this test is included for branch completeness
    """
    patch_events: List[Event] = [
        events.on_message,
        events.on_command,
        events.on_message_raw
    ]

    # patch out existing subscribers, they are irrelevant
    for event in patch_events:
        monkeypatch.setattr(event, "subscribers", [])

    monkeypatch.setattr(bot_fx, "graceful_errors", False)

    @events.on_message.subscribe
    async def boomstick(*args, **kwargs):
        """ goes boom"""
        raise RuntimeError

    with raises(RuntimeError):
        await bot_fx.on_message("#unit_testing", "some_recruit", "💥stick")


@mark.asyncio
async def test_on_connect(bot_fx, monkeypatch, async_callable_fx):
    """
    Verify behavior of MechaClient.on_connect
    """

    async_callable_fx.return_value = True

    # patch the Pydle call, its out of scope
    monkeypatch.setattr(bot_fx, "join", async_callable_fx)

    event_mock = AsyncCallableMock()

    # hook into the raised event
    events.on_connect.subscribe(event_mock)
    # call the function
    await bot_fx.on_connect()

    assert async_callable_fx.was_called

    # assert the bot joined the correct number of channels
    assert len(async_callable_fx.calls) == len(config["irc"]["channels"])

    # ensure the event got raised
    assert event_mock.was_called
    # and only once
    assert event_mock.was_called_once

    # assert we joined the channels we thought we did
    for channel in config["irc"]["channels"]:
        assert async_callable_fx.was_called_with(channel)


@mark.asyncio
async def test_on_nick_change(bot_fx, async_callable_fx):
    """
    verifies behavior of MechaClient.on_nick_change
    """
    events.on_nick_change.subscribe(async_callable_fx)

    old = "rat_4288"
    new = "PizzaLover9000"
    await bot_fx.on_nick_change(old, new)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(old=old, new=new, bot=bot_fx)


@mark.asyncio
async def test_on_part(async_callable_fx, bot_fx):
    """
    Verifies behavior of MechaClient.on_part
    """

    # hook into the event that should be raised
    events.on_part.subscribe(async_callable_fx)
    kwargs = {
        "channel": "#ratchat",
        "user": "some_ov",
        "reason": "Running from NDs and toward 🍫",
    }
    await bot_fx.on_part(**kwargs)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(**kwargs, bot=bot_fx)


@mark.asyncio
async def test_on_private_message(async_callable_fx, bot_fx):
    """
    Verify behavior of Mechaclient.on_private_message
    """
    events.on_private_message.subscribe(async_callable_fx)

    kwargs = {
        "sender": "some_ov",
        "message": "!list"
    }
    await bot_fx.on_private_message(**kwargs)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(context=InstanceOf(Context))


@mark.asyncio
async def test_topic_change(bot_fx, async_callable_fx):
    events.on_topic_change.subscribe(async_callable_fx)
    kwargs = {
        "channel": "#ratchat",
        "topic": "Ladies and Gentlerats, Whitesheets has entered the building",
        "author": "some_ov"
    }
    await bot_fx.on_topic_change(**kwargs)
    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    # this method uses a different kwarg than what we give it
    # so we mutate the dict so it matches the expected output
    del kwargs["author"]
    kwargs["user"] = await User.from_whois(bot_fx, "some_ov")
    assert async_callable_fx.was_called_with(**kwargs, bot=bot_fx)


@mark.asyncio
async def test_on_quit(async_callable_fx, bot_fx):
    events.on_quit.subscribe(async_callable_fx)
    kwargs = {
        "user": "some_recruit",
        "message": "Ladies and Gentlemen, "
                   "I am afraid we are going down."
                   "Im afraid we are going down in flames."
    }

    await bot_fx.on_quit(**kwargs)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(**kwargs, bot=bot_fx)
