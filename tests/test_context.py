"""
test_context.py - Tests for Context

test suite for the Context module

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import pytest

from Modules import context
from Modules.user import User

pytestmark = pytest.mark.context


@pytest.mark.asyncio
@pytest.mark.usefixtures('context_fx')
async def test_reply(bot_fx):
    """
    Verifies `context.reply` functions as expected

    Args:
        context_fx ():

    Returns:

    """
    payload = "This is my reply!!!!"

    context.target.set("#unit_test")
    # make the call
    await context.reply(payload)

    assert payload == bot_fx.sent_messages[0]['message']


@pytest.mark.parametrize("channel, user, message, words, words_eol, prefixed",
                         [
                             [
                                 "#unit_test", "unit_test", "!snafu", ['snafu'], ['snafu'], True
                             ],
                             [
                                 "#ratchat", "some_ov", "!foo bar", ['foo', 'bar'],
                                 ['foo bar', 'bar'], True
                             ],
                             [
                                 "#unit_test", "unit_test[bot]", "I wonder...", ["I", "wonder..."],
                                 ["I wonder...", "wonder..."], False
                             ],
                             [
                                 "#badlands", "some_recruit", "ive been a baad boy!",
                                 ['ive', 'been', 'a', 'baad', 'boy!'],
                                 ['ive been a baad boy!', 'been a baad boy!', 'a baad boy!',
                                  'baad boy!', 'boy!'], False
                             ]
                         ])
@pytest.mark.asyncio
@pytest.mark.usefixtures('context_fx')
async def test_from_message(bot_fx, channel, user, message, words, words_eol, prefixed):
    context.bot.set(bot_fx)
    context.target.set(channel)
    context.message.set(message)
    context.sender.set(user)

    # run the target
    await context.from_message()
    if prefixed:
        assert context.prefixed.get()
    else:
        assert not context.prefixed.get()

    assert channel == context.channel.get()
    assert User(**bot_fx.users[user]) == context.user.get()
    assert words == context.words.get()
    assert words_eol == context.words_eol.get()
