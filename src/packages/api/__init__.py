"""
__init__.py -

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from src.config import PLUGIN_MANAGER
from .api_manager import APIManager, ApiOfflineError

__all__ = ["APIManager", "ApiOfflineError"]

PLUGIN_MANAGER.register(APIManager, "api_manager")
