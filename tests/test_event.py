"""
test_event.py - Event system testing

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import pytest

from Modules.events.event import Event


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

        await Event.events['on_wizard_search'].emit(12, hotel=22)

        assert len(fired_list) == 1
        args, kwargs = fired_list[0]
        assert args == (12,)
        assert kwargs == {'hotel': 22}

    async def test_create_event_bad_type(self):
        """ verifies the result when somone tries to create an event with an invalid coro type"""
        with pytest.raises(TypeError):
            Event(None)
