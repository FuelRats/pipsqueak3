"""
test_administration.py  - tests for the administration command suite

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging

from src.commands import administration
from src.packages.context import Context

LOG = logging.getLogger(f"mecha.{__name__}")
import pytest


@pytest.mark.asyncio
async def test_rehash_dm(context_pm_fx, bot_fx, async_callable_fx, monkeypatch):
    """
    Verifies rehash tells off the user when they attempt to invoke the command in private.
    """

    monkeypatch.setattr(administration, "setup", async_callable_fx)
    async_callable_fx.return_value = ({}, '22aa')

    await administration.cmd_rehash(context_pm_fx)

    assert "everyone can see" in bot_fx.sent_messages[0]['message']
    assert not async_callable_fx.was_called


@pytest.mark.asyncio
async def test_rehash_not_authorized(bot_fx, async_callable_fx, monkeypatch):
    context = await Context.from_message(bot_fx, "#unittest", "some_recruit", "!rehash 👿")

    monkeypatch.setattr(administration, "setup", async_callable_fx)
    async_callable_fx.return_value = ({}, '22aa')

    await administration.cmd_rehash(context=context)

    assert "no." == bot_fx.sent_messages[0]['message']
    assert not async_callable_fx.was_called


@pytest.mark.parametrize("exc_class", (ValueError, KeyError))
@pytest.mark.asyncio
async def test_rehash_application_failure(bot_fx, async_callable_fx, monkeypatch, exc_class,
                                          context_channel_fx, caplog):
    """
    verifies the commands behavior when the setup() call fails (predictably).
    """
    context = await Context.from_message(bot_fx, "#unittest", "some_admin", "!rehash")

    def boom(*args, **kwargs):
        raise exc_class

    monkeypatch.setattr(administration, "setup", boom)

    await administration.cmd_rehash(context)

    assert "unable to rehash configuration" in bot_fx.sent_messages[1]['message']
