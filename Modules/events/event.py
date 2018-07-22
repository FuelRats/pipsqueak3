"""
event.py - Event system

A Class decorator event system.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging
from functools import partial
from typing import Callable, List, Dict, Any, Union

# typedef
subscriptions = List[Callable]
log = logging.getLogger(f"mecha.{__name__}")

# If a subscriber returns this value, the event will canceled.
# return this value to consume an event
CANCEL_EVENT = object()


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

    async def _emit(self, *args, **kwargs):
        """
        async generator that does the actual event emission

        Args:
            *args ():
            **kwargs ():

        Yields:
            return value of each subscriber
        """
        for subscriber in self.subscribers:
            log.debug(f"calling subscriber {subscriber}...")
            result = await subscriber(*args, **kwargs)
            if result is CANCEL_EVENT:
                return  # cancel the generator

            yield result

    async def emit(self, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Emit the event to all subscribers

        Args:
            *args (tuple): tuple of positional arguments to subscribers
            **kwargs (dict): dict of keyword arguments to provide to subscribers

        Returns:

        """
        outcomes = [outcome async for outcome in self._emit(*args, **kwargs)]
        log.debug(f"outcomes = {outcomes}")
        return outcomes

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

    def subscribe(self, coro: Union[Callable, partial]) -> Callable:
        """
        Subscribe to this event

        This method can be used as a decorator around **static methods**

        To subscribe to an **instance** method, please call subscribe directly (see examples)

        Args:
            coro(Callable): async def function to make a subscriber

            coro(partial): pre-prepared partial to make a subscriber

        Raises:
            ValueError: attempted to subscribe to an event that is not registered

        Examples:
            any async function can use this decorator to subscribe to an **existing** event
            Further, the decorator form can only be used on static methods due tech limitations.

            >>> event = Event("subscribe_example_event")
            >>> @event.subscribe
            ... async def subscribe_demo_coro(*args, **kwargs):
            ...     print("woohoo!")
            ...     return 42
            >>> subscribe_demo_coro in event.subscribers
            True

            As a subscriber, the decorated function will be called during the Events `emit` phase
            >>> import asyncio
            >>> loop = asyncio.get_event_loop()
            ... # setup an asyncio event loop, so we can run our event
            >>> loop.run_until_complete(event.emit())
            woohoo!
            [42]

            To add a **instance** method as a subscriber, or to otherwise pre-prepare a function,
            this method can be passed a partial.
            >>> del event  # cleanup from last doctest
            >>> from functools import partial
            ...
            >>> event = Event("subscribe_partial_event")
            >>> async def subscribe_partial(*args, **kwargs):
            ...     return 12
            >>> my_partial = partial(subscribe_partial)
            >>> _ = event.subscribe(my_partial)

            >>> my_partial in event.subscribers
            True

        Notes:
            - all subscribers must be asynchronous function definitions as they will be awaited

            - subscribers will be served on a first-in-first-out basis.
        """

        self.subscribers.append(coro)
        return coro
