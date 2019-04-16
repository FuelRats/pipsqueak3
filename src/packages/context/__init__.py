"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from src.config import plugin_manager
from . import context
from .context import Context

__all__ = ["Context"]

plugin_manager.register(context, "context")
