"""
test_offline_abc.py - Tests for the Core offline implementation

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from typing import NoReturn

import pytest

from Modules.offline_awareness import OfflineAwareABC

pytestmark = pytest.mark.offline


class Aware(OfflineAwareABC):
    async def on_online(self) -> NoReturn:
        ...

    async def on_offline(self) -> NoReturn:
        ...


@pytest.fixture
def offline_aware_fx(async_callable_fx) -> OfflineAwareABC:
    class AwareFixture(OfflineAwareABC):
        async def on_online(self) -> NoReturn:
            await async_callable_fx("online")

        async def on_offline(self) -> NoReturn:
            await async_callable_fx("offline")

    return AwareFixture()


def test_offline_makes_weakref(offline_aware_fx):
    """
    Verifies instantiating a offline aware subclass creates a weak reference in the superclass.
    """
    # assert our weak reference actually exists
    assert offline_aware_fx is OfflineAwareABC._storage[0].peek()[0]


def test_multiple_init():
    # spawn a couple instances
    instance1 = Aware()
    instance2 = Aware()

    references = [finalizer.peek()[0] for finalizer in OfflineAwareABC._storage]
    assert instance2 in references
    assert instance1 in references


def test_cleanup():
    """
    Verifies dead weak references are cleaned up automatically
    """

    # make a instance
    instance = Aware()

    # make a second instance that we won't immediately dispose of
    instance2 = Aware()

    # assert we got our weak references
    assert 2 == len(OfflineAwareABC._storage), "Instances never got their weak reference"

    # remove `instance`'s last strong reference, causing it to get GC'ed
    del instance

    # assert the weak reference got culled as it died.
    assert 1 == len(OfflineAwareABC._storage), "Instance weak reference never got culled"


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ['online', 'offline'])
async def test_invocation(offline_aware_fx, async_callable_fx, mode: str):
    """
    Verifies going online propagates to offline-aware class instances
    """

    # ensure correct state for test
    OfflineAwareABC.online = mode == "offline"

    action = getattr(OfflineAwareABC, f"go_{mode}")
    await action()

    assert async_callable_fx.was_called, "child class never got its on_online event called!"

    assert async_callable_fx.was_called_once, "event got called multiple times!"

    assert async_callable_fx.was_called_with(mode), "wrong event called! (check on_online," \
                                                    " on_offline)"


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ['online', 'offline'])
async def test_idempotency(offline_aware_fx, async_callable_fx, mode: str):
    """
    Verifies `go_online` is idempotent
    """
    # ensure correct state for test
    OfflineAwareABC.online = mode == "offline"

    action = getattr(OfflineAwareABC, f"go_{mode}")
    await action()
    # call it a second time
    await action()

    assert async_callable_fx.was_called, "child class never got its on_online event called!"

    # assert we only got called once, asserting idempotency
    assert async_callable_fx.was_called_once, "event got called multiple times!"

    assert async_callable_fx.was_called_with(mode), "wrong event called! (check on_online," \
                                                    " on_offline)"
