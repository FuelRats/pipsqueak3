"""
event.py - Event system

A Class decorator event system.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging
from typing import Callable, List, Dict, Any

# typedef
subscriptions = List[Callable]
log = logging.getLogger(f"mecha.{__name__}")


class Event:
    """
        Defines an event.

        an event is a subscribe-able object that will call its subscribers when it is invoked.

        Subscription is possible by using the `@Event.subscribe` decorator

    Examples:

         an event can also be defined without a function definition
         >>> my_other_event = Event("my_other_event")
         >>> "my_other_event" in Event.events
         True

         Notes:
             - Events will need to be invoked by something.

             - Event subscribers must be async functions, and should be tested to work with
             the event's signature (variable)

             - exceptions raised by subscribers will not stop an event from being emitted

             - the return value of decorated events are discarded.

    """
    events: Dict[str, 'Event'] = {}
    """Registry mapping event names to their subscribers"""

    def __init__(self, name: str):
        """
        Defines a new Event

        Args:
            name (str): name of the new event
        """
        if not isinstance(name, str):
            raise TypeError(f"expected type str got {type(name)}")
        self.name = name
        """name of this event"""
        self.subscribers: subscriptions = []
        """This events subscribers"""

        Event._register(self)

    async def emit(self, *args: Any, **kwargs: Any):
        """
        Emit the event to all subscribers
        Args:
            *args (tuple): tuple of positional arguments to subscribers
            **kwargs (dict): dict of keyword arguments to provide to subscribers

        Returns:

        """
        for subscriber in self.subscribers:
            log.debug(f"calling subscriber {subscriber}...")
            await subscriber(*args, **kwargs)

    @classmethod
    def _register(cls, event: 'Event'):
        """
        Registers a new event

        Args:
            event(Event): Event to register

        Raises:
            ValueError: attempted to register an event has already been registered
        """
        if event.name in cls.events:
            raise ValueError(f"name {event.name} is already registered as an event")
        cls.events[event.name] = event

    def subscribe(self, coro):
        """
        Subscribe to this event

        Raises:
            ValueError: attempted to subscribe to an event that is not registered

        Examples:
            any async function can use this decorator to subscribe to an **existing** event

            >>> event = Event("subscribe_example_event")
            >>> @event.subscribe
            ... async def subscribe_demo_coro(*args, **kwargs):
            ...     print("woohoo!")
            >>> subscribe_demo_coro in event.subscribers
            True

            As a subscriber, the decorated function will be called during the Events `emit` phase
            >>> import asyncio
            >>> loop = asyncio.get_event_loop()
            ... # setup an asyncio event loop, so we can run our event
            >>> loop.run_until_complete(event.emit())
            woohoo!


        Notes:
            - any values returned by subscribers will be discarded.

            - all subscribers must be asynchronous function definitions as they will be awaited

            - subscribers will be served on a first-in-first-out basis.
        """

        self.subscribers.append(coro)
        return coro
