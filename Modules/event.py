"""
event.py - Event system

A Class decorator event system.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging
from typing import Callable, List, Dict

# typedef
subscriptions = List[Callable]
log = logging.getLogger(f"mecha.{__name__}")


class Event:
    """
    Registers a async function as an event.

    The registered event will be the name of the decorated function.

    Examples:
         >>> @Event
         ... async def my_event(*args, **kwargs):
         ...    pass
         >>> "my_event" in Event.events
         True
    """
    events: Dict[str, subscriptions] = {}
    """Registry mapping event names to their subscribers"""

    def __init__(self, coro: Callable):
        log.debug(f"decorating coro {coro}")
        self.decorated_coro = coro
        self.name = coro.__name__
        Event._register(self.name)

    async def _emit(self, *args, **kwargs):
        """Emit an event to all subscribers"""
        for subscriber in self.events[self.decorated_coro.__name__]:
            log.debug(f"calling subscriber {subscriber}...")
            await subscriber(*args, **kwargs)

    async def __call__(self, *args, **kwargs):
        log.debug(f"called with args {args} and kwargs {kwargs}")
        await self.decorated_coro(*args, **kwargs)
        log.debug(f"emitting event to subscribers...")
        await self._emit(*args, **kwargs)

    @classmethod
    def _register(cls, name: str):
        """
        Registers a new event

        Args:
            name (str): name of event to register

        Raises:
            ValueError: attempted to register an event has already been registered
        """
        if name in cls.events:
            raise ValueError(f"name {name} is already registered as an event. "
                             f"please choose a different name")
        cls.events[name] = []

    class Subscribe:
        """
        Subscribe to an event (this is a decorator)
        """

        def __init__(self, event: str):
            if event not in Event.events.keys():
                raise ValueError(f"event '{event}' is not a registered event.")
            log.debug(f"subscribing to {event}...")
            self.event = event

        def __call__(self, coro: Callable):
            Event.events[self.event].append(coro)
