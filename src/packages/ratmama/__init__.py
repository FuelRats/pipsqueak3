"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
__all__ = ["handle_ratmama_announcement", "handle_ratsignal"]
from src.config import PLUGIN_MANAGER
from .ratmama_parser import handle_ratmama_announcement, handle_ratsignal
from . import ratmama_parser as _parser

PLUGIN_MANAGER.register(_parser, "ratmama_parser")
