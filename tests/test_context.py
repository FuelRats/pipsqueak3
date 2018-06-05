"""
test_context.py - Tests for Context

test suite for the Context module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from Modules.context import Context


def test_constructor(bot_fx, User_fx):
    """verifies the constructor functions"""
    my_context = Context(User_fx, bot_fx, "#unittest", ["bird", "is", "the", "word"], [""])

    assert my_context.bot is bot_fx
    assert my_context.channel == "#unittest"
    assert my_context.words == ["bird", "is", "the", "word"]
    assert my_context.words_eol == [""]
    assert my_context.user == User_fx


def test_channel_true(Context_channel_fx: Context):
    """Verifies the Context.channel function behaves as expected in a channel context"""
    assert Context_channel_fx.channel == "#unit_test"


def test_channel_false(Context_pm_fx: Context):
    """Verifies Context.channel behaves as expected in a PM context"""
    assert Context_pm_fx.channel is None
