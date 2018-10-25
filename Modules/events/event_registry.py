"""
event_registry.py - Central repository for pre-defined events

This module contains the definitions for all pre-defined events

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

"""
from Modules.events import Event

# MechaClient related events
on_connect = Event("on_connect")
on_join = Event("on_join")
on_user_mode_change = Event("on_user_mode_change")

# message related events
on_message_raw = Event("on_message_raw")
on_message = Event("on_message")
on_command = Event("on_command")
on_channel_message = Event("on_channel_message")

# user events
on_kill = Event("on_kill")
on_kick = Event("on_kick")
on_quit = Event("on_quit")
on_mode_change = Event("on_mode_change")
on_nick_change = Event("on_nick_change")

# channel events
on_part = Event("on_part")
on_private_message = Event("on_private_message")
on_invite = Event("on_invite")
on_topic_change = Event("on_topic_change")
