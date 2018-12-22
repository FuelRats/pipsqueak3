"""
__init__.py.py - Context-sensitive variables

Provides an interface for tending to context-sensitive data such as cross-function execution context

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from ._context import message, user, target, channel, prefixed, bot, words_eol, words, sender, \
    from_message, reply

__all__ = [
    "message",
    'user',
    'target',
    'channel',
    'prefixed',
    'bot',
    'words',
    'words_eol',
    'sender',
    'from_message',
    'reply'
]
