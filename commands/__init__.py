"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
__all__ = []

if __debug__:
    from . import debug
    __all__.append('debug')
