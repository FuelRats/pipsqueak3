"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from src.config import PLUGIN_MANAGER
from . import context
from .context import Context

__all__ = ["Context"]

PLUGIN_MANAGER.register(context, "context")
