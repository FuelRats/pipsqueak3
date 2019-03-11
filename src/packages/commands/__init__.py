"""
commands.__init__.py  - commands package

provides command registration and handling code.

Copyright (c) $DateTime.year The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from .rat_command import command, trigger

__all__ = ["command", "trigger"]
