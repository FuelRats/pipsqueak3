"""
test_administration.py  - tests for the administration command suite

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging

from src.commands import administration
from src.packages.commands import trigger
from src.packages.context import Context

import pytest
import string

pytestmark = [pytest.mark.unit, pytest.mark.commands]

@pytest.mark.asyncio
async def test_rehash_dm(context_pm_fx, bot_fx, callable_fx, monkeypatch):
    """
    Verifies rehash tells off the user when they attempt to invoke the command in private.
    """

    monkeypatch.setattr(administration, "setup", callable_fx)
    callable_fx.return_value = ({}, '22aa')
    ctx = await Context.from_message(
        bot_fx, channel="non_channel",
        sender="some_admin", message="!rehash"
    )
    await trigger(ctx=ctx)

    assert "everyone can see" in bot_fx.sent_messages[0]['message']
    assert not callable_fx.was_called


@pytest.mark.asyncio
async def test_rehash_not_authorized(bot_fx, callable_fx, monkeypatch):
    context = await Context.from_message(bot_fx, "#unittest", "some_recruit", "!rehash 👿")

    monkeypatch.setattr(administration, "setup", callable_fx)
    callable_fx.return_value = ({}, '22aa')

    ctx = await Context.from_message(
        bot_fx, channel="non_channel",
        sender="some_recruit", message="!rehash"
    )
    await trigger(ctx)

    assert "no." == bot_fx.sent_messages[0]['message']
    assert not callable_fx.was_called


@pytest.mark.parametrize("exc_class", (ValueError, KeyError))
@pytest.mark.asyncio
async def test_rehash_application_failure(bot_fx, callable_fx, monkeypatch, exc_class, ):
    """
    verifies the commands behavior when the setup() call fails (predictably).
    """
    context = await Context.from_message(bot_fx, "#unittest", "some_admin", "!rehash")

    def boom(*args, **kwargs):
        raise exc_class

    monkeypatch.setattr(administration, "setup", boom)

    await administration.cmd_rehash(context)

    assert "unable to rehash configuration" in bot_fx.sent_messages[1]['message']


@pytest.mark.asyncio
async def test_rehash_successful(bot_fx, callable_fx, monkeypatch):
    """
    successful invocation test
    """
    context = await Context.from_message(bot_fx, "#unittest", "some_admin", "!rehash")

    some_checksum = string.ascii_letters[:8]
    callable_fx.return_value = ({}, 'abcdefghijk')
    monkeypatch.setattr(administration, "setup", callable_fx)

    await administration.cmd_rehash(context)

    # assert the hash is in the message
    assert some_checksum in bot_fx.sent_messages[1]['message']
    # and that success is
    assert "success" in bot_fx.sent_messages[1]['message']
