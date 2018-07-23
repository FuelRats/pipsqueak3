"""
test_event.py - Event system testing

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from functools import partial

import pytest

from Modules.events import CANCEL_EVENT
from Modules.events import Event


@pytest.mark.usefixtures("clear_events")
@pytest.mark.event_system
@pytest.mark.asyncio
class TestEvents:
    """Tests for the event system"""

    @pytest.mark.parametrize("name", ["on_message", "on_join", "on_command"])
    async def test_register_declaration(self, name: str):
        """Verifies that events can be declared into existance via the event = Event(name) method"""
        event = Event(name)
        assert name in Event.events
        assert name == event.name

    async def test_declared_event_subscription(self):
        """Verifies an declared event can be subscribed to.

        (this test focuses on declared events)
        """
        fired_list = []

        event = Event("on_wizard_search")

        @event.subscribe
        async def my_subscriber(*args, **kwargs):
            fired_list.append((args, kwargs))

        await event.emit(12, hotel=22)

        assert len(fired_list) == 1
        args, kwargs = fired_list[0]
        assert args == (12,)
        assert kwargs == {'hotel': 22}

    async def test_generic_event_subscription(self):
        """Verifies an declared event can be subscribed to (both varients tested here)"""
        fired_list = []

        event = Event("on_wizard_search")

        @event.subscribe
        async def my_subscriber(*args, **kwargs):
            fired_list.append((args, kwargs))

        await event.emit(12, hotel=22)

        assert len(fired_list) == 1
        args, kwargs = fired_list[0]
        assert args == (12,)
        assert kwargs == {'hotel': 22}

    async def test_create_event_bad_type(self):
        """ verifies the result when somone tries to create an event with an invalid coro type"""
        with pytest.raises(TypeError):
            Event(None)

    async def test_subscribe_partial(self):
        """ verifies partial functions can be subscribers"""
        retn = []
        event = Event("unit_test_event")

        async def test_callback(*args):
            retn.append(args)

        my_partial = partial(test_callback, 22)
        event.subscribe(my_partial)

        assert my_partial in event.subscribers

    async def test_manual_suscribe_invoked_on_emit(self):
        """verifies that when making a manual subscription, the subscriber still gets invoked"""
        retn = []
        event = Event("unit_test_event")

        async def test_callback(*args):
            retn.append(args)

        my_partial = partial(test_callback, 22)
        event.subscribe(my_partial)

        await event.emit(2)
        assert retn[0] == (22, 2)

    async def test_event_cancellation(self):
        """
        Verifies event cancellation actually works.
        """
        event = Event("unit-test-event")

        # register a bunch of events

        @event.subscribe
        async def a():
            return "oh no..."

        @event.subscribe
        async def b():
            return "FIRE IN THE HOLE!"

        # plant a bomb
        @event.subscribe
        async def bomb():
            return CANCEL_EVENT

        # place an observer of the aftermath
        @event.subscribe
        async def rubble():
            return "I don't wanna return!"

        results = await event.emit()

        assert len(results) == 2
        assert results == ['oh no...', "FIRE IN THE HOLE!"]
        assert "I don't wanna return!" not in results

