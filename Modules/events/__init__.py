"""
__init__.py - The Event system namespace

This package contains the Event system and all known events as of compile time.

Events created at runtime will not show up here, it is recommended you add the event declarations
 to the :mod:`event_registry` as to avoid nasty chicken-egg import errors.

:class:`Event`:
----------------
    This class defines an Event, to which other functions can subscribe to. see :class:`Event`
    for a full description

:obj:`CANCEL_EVENT`:
-----------------
    a subscriber can return this sentinel value to cancel the subscribed event.
    Any subsequent subscribers for the canceled event will not be called.


Known events (:mod:`event_registry`):
----------------
on_connect (:class:`Event`): Called when the MechaClient completes a server connection

on_user_mode_change (:class:`Event`):The MechaClient's modes got changed

on_private_message (:class:`Event`):invoked when the MechaClient receives a direct message

on_private_notice (:class:`Event`):invoked when the MechaClient recieves a notice in a channel

on_invite (:class:`Event`): invoked when the MechaClient receives an invite

on_message_raw (:class:`Event`): invoked prior to any handling on any message (channel or DM)

on_message (:class:`Event`): invoked if the incoming message is not a command (channel or DM)

on_command (:class:`Event`): invoked if the incoming message is a command invocation(channel or DM)

on_notice (:class:`Event`): invoked when the MechaClient recieves a notice of any kind

on_channel_notice (:class:`Event`): invoked when the MechaClient recieves a notice in a direct message

on_channel_message (:class:`Event`): invoked when a message is received in a channel

on_topic_change (:class:`Event`): a channels topic got changed

on_mode_change (:class:`Event`): a channels modes got changed

on_kill (:class:`Event`): a user was killed

on_kick (:class:`Event`): a user was kicked from a channel

on_quit (:class:`Event`): a user quit a channel

on_nick_change (:class:`Event`): a user changed nicknames

on_part (:class:`Event`): a user left a channel gracefully

on_join (:class:`Event`): a user joined a channel


----------


Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from .event import Event, CANCEL_EVENT
from .event_registry import *

__all__ = ['Event',
           'CANCEL_EVENT',
           "on_message",
           "on_message_raw",
           "on_channel_message",
           "on_command",
           "on_connect",
           "on_join",
           "on_channel_notice",
           "on_invite",
           "on_nick_change",
           "on_kill",
           "on_kick",
           "on_quit",
           "on_mode_change",
           "on_part",
           "on_private_message",
           "on_private_notice",
           "on_topic_change",
           "on_user_mode_change"
           ]
