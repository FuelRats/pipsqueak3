"""
test_context.py - Tests for Context

test suite for the Context module

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import pytest

from src.packages.context.context import Context

pytestmark = [pytest.mark.unit, pytest.mark.context]


def test_constructor(bot_fx, user_fx):
    """verifies the constructor functions"""
    my_context = Context(bot_fx, user_fx, "#unittest", ["bird", "is", "the", "word"], [""])

    assert my_context.bot is bot_fx
    assert my_context.channel == "#unittest"
    assert my_context.words == ["bird", "is", "the", "word"]
    assert my_context.words_eol == [""]
    assert my_context.user == user_fx


def test_channel_true(context_channel_fx: Context):
    """Verifies the Context.channel function behaves as expected in a channel context"""
    assert context_channel_fx.channel == "#unit_test"


def test_channel_false(context_pm_fx: Context):
    """Verifies Context.channel behaves as expected in a PM context"""
    assert context_pm_fx.channel is None


@pytest.mark.asyncio
async def test_reply(context_fx: Context):
    """
    Verifies `context.reply` functions as expected

    Args:
        context_fx ():

    Returns:

    """
    payload = "This is my reply!!!!"

    # make the call
    await context_fx.reply(payload)

    assert payload == context_fx.bot.sent_messages[0]['message']


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
                                 "#unit_test", "unit_test[BOT]", "I wonder...", ["I", "wonder..."],
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
async def test_from_message(bot_fx, channel, user, message, words, words_eol, prefixed):
    ctx = await Context.from_message(bot_fx, channel, user, message)

    if prefixed:
        assert ctx.prefixed
    else:
        assert not ctx.prefixed

    assert channel == ctx.channel
    assert user == ctx.user.nickname
    assert words == ctx.words
    assert words_eol == ctx.words_eol
