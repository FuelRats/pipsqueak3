"""
test_infrastructure.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import pytest

from Modules import permissions
from Modules.context import Context

pytestmark = pytest.mark.registry


def test_command_registration(command_registry_fx):
    @command_registry_fx.register("foo", "bar")
    async def test_cmd(*args, **kwargs):
        ...

    # assert our name are in the registry
    assert "foo" in command_registry_fx
    assert "bar" in command_registry_fx

    # assert our underlying was registered
    assert command_registry_fx['foo'].underlying is test_cmd


@pytest.mark.asyncio
async def test_underlying_callable(command_registry_fx, async_callable_fx):
    # more trivial than attempting a monkeypatch
    command_registry_fx._commands['mock'] = async_callable_fx
    await command_registry_fx['mock'](None)

    assert async_callable_fx.was_called


def test_require_dm_and_channel_mutually_exclusive(command_registry_fx):
    with pytest.raises(ValueError, match="require_dm and require_channel are mutually exclusive."):
        @command_registry_fx.register("guarded", require_dm=True, require_channel=True)
        async def guarded():
            ...


@pytest.mark.asyncio
async def test_require_dm(command_registry_fx, async_callable_fx, context_pm_fx,
                          context_channel_fx):
    @command_registry_fx.register("catnip", require_dm=True)
    async def _():
        ...

    # set the underlying to the mock, note .underlying isn't settable and is intended to be
    # immutable at runtime. test hax
    command_registry_fx['catnip']._underlying = async_callable_fx

    await command_registry_fx['catnip'](context_channel_fx)

    assert not async_callable_fx.was_called

    await command_registry_fx['catnip'](context_pm_fx)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once


@pytest.mark.asyncio
async def test_require_channel(command_registry_fx, async_callable_fx, context_pm_fx,
                               context_channel_fx):
    @command_registry_fx.register("bear_trap", require_channel=True)
    async def _():
        ...

    # set the underlying to the mock, note .underlying isn't settable and is intended to be
    # immutable at runtime. test hax
    command_registry_fx['bear_trap']._underlying = async_callable_fx

    await command_registry_fx['bear_trap'](context_pm_fx)

    assert not async_callable_fx.was_called

    await command_registry_fx['bear_trap'](context_channel_fx)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once


@pytest.mark.asyncio
async def test_require_permission_lesser(async_callable_fx,
                                         command_registry_fx,
                                         bot_fx):
    """
    asserts calling a callable protected by require_permission without the requisite permission
    fails.
    """

    @command_registry_fx.register('guarded', require_permission=permissions.OVERSEER)
    async def guarded(*args, **kwargs):
        assert False, "guarded should not be callable"

    ctx = await Context.from_message(bot_fx, "#unit_test", "some_recruit",
                                     "guarded oh guarded! reveal your secrets to me!")

    await command_registry_fx['guarded'](context=ctx)


@pytest.mark.asyncio
async def test_require_permission_ge(async_callable_fx,
                                     command_registry_fx,
                                     bot_fx):
    """
    asserts calling a callable protected by require_permission  with necessary permissions works.
    """

    @command_registry_fx.register('guarded', require_permission=permissions.OVERSEER)
    async def guarded(*args, **kwargs):
        await async_callable_fx(*args, **kwargs)

    ctx = await Context.from_message(bot_fx, "#unit_test", "some_ov",
                                     "guarded oh guarded! reveal your secrets to me!")

    await command_registry_fx['guarded'](context=ctx)

    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_once
