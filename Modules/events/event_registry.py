"""
event_registry.py - Central repository for pre-defined events

This module contains the definitions for all pre-defined events

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from Modules import events

on_message = events.Event("on_message")
on_command = events.Event("on_command")
on_join = events.Event("on_join")
on_connect = events.Event("on_connect")
on_message_raw = events.Event("on_message_raw")
