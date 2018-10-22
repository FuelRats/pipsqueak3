"""
test_mechaClient.py - tests for the MechaClient
Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from pytest import mark

from Modules.context import Context
from Modules.events import event_registry
from tests.mock_callables import InstanceOf

pytestmark = mark.mecha


@mark.asyncio
async def test_on_message(async_callable_fx, bot_fx):
    event_registry.on_message.subscribe(async_callable_fx)

    await bot_fx.on_message("#unit_test", "unit_test", "hi there!")

    assert async_callable_fx.was_called


@mark.asyncio
async def test_on_notice(async_callable_fx, bot_fx):
    event_registry.on_notice.subscribe(async_callable_fx)

    await bot_fx.on_notice("#unit_test", "unit_test", "hi there!")

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_with(context=InstanceOf(Context))


@mark.asyncio
async def test_on_channel_notice(async_callable_fx, bot_fx):
    event_registry.on_channel_message.subscribe(async_callable_fx)

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
    event_registry.on_invite.subscribe(async_callable_fx)

    channel = "#invite_test"
    sender = "unit_test"
    await bot_fx.on_invite(channel, sender)

    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(channel=channel, sender=sender, bot=bot_fx)


@mark.asyncio
async def test_on_kick(async_callable_fx, bot_fx):
    event_registry.on_kick.subscribe(async_callable_fx)
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
    event_registry.on_kill.subscribe(async_callable_fx)
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
    event_registry.on_mode_change.subscribe(async_callable_fx)

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
    event_registry.on_message.subscribe(async_callable_fx)
    # lets also hook it into on_command, just to be sure
    event_registry.on_command.subscribe(async_callable_fx)

    # call the method
    retn = await bot_fx.on_message("#unit_test", bot_fx.nickname, "potato")

    # ensure the callable didn't get called anyways
    assert not async_callable_fx.was_called

    # ensure we got the expected return type
    assert retn is None
