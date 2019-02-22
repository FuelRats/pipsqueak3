"""
__init__.py - Offline awareness base implementation

Provides a ABC and an interface for offline-aware components.
Specifically, this module provides the :class:`OfflineAwareABC` base class, which provides an
interface and signalling primitive for offline-aware classes.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from ._offline_aware_abc import OfflineAwareABC

# convenience aliases
online = OfflineAwareABC.go_online
"""
Move the system to online mode, alias to :class:`OfflineAwareABC`.go_online

This function is Idempotent
"""
offline = OfflineAwareABC.go_offline
"""
Move the system to offline mode, alias to :class:`OfflineAwareABC`.go_offline

This function is Idempotent
"""

__name__ = [
    "OfflineAwareABC",
    "online",
    "offline"
]
