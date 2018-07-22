"""
test_event.py - Event system testing

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import pytest

from Modules.event import Event


@pytest.mark.usefixtures("clear_events")
@pytest.mark.event_system
@pytest.mark.asyncio
class TestEvents:
    """Tests for the event system"""

    async def test_register_decoration(self):
        """Tests that events are correctly registered via the @Event method"""

        @Event
        async def my_event(*args, **kwargs):
            ...

        assert 'my_event' in Event.events

    @pytest.mark.parametrize("name", ["on_message", "on_join", "on_command"])
    async def test_register_declaration(self, name: str):
        """Verifies that events can be declared into existance via the event = Event(name) method"""
        event = Event(name)
        assert name in Event.events
        assert name == event.name

    # async def test_decorated_invocation(self):
    #     """Ensures a decorated function gets invoked when the event is fired"""
    #
    #     fired = False
    #
    #     @Event
    #     async def my_event(*args, **kwargs):
    #         global fired
    #         fired = True
    #     Event.events['my_event'].
    #     assert fired