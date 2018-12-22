"""
_context.py - Command contexts

Provides Context Variables and context-sensitive utilities

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from contextvars import ContextVar
from typing import Optional, Tuple, List, TYPE_CHECKING

from Modules.user import User
from config import config

if TYPE_CHECKING:
    from main import MechaClient
target: ContextVar[str] = ContextVar('target')
channel: ContextVar[str] = ContextVar('channel', default=None)
user: ContextVar[User] = ContextVar('user')
words: ContextVar[List[str]] = ContextVar('words')
words_eol: ContextVar[List[str]] = ContextVar('words_eol')
prefixed: ContextVar[bool] = ContextVar('prefixed', default=False)
message: ContextVar[str] = ContextVar('message')
bot: ContextVar['MechaClient'] = ContextVar('bot')
sender: ContextVar[str] = ContextVar('sender')

_prefix = config['commands']['prefix']


async def from_message():
    """
    Populates the context from a IRC message
    """
    _message = message.get()
    _bot = bot.get()
    # check if the message has our prefix
    _prefixed = _message.startswith(_prefix)

    if _prefixed:
        prefixed.set(_message.startswith(_prefix))
        # before removing it from the message
        _message = _message[len(_prefix):]
        message.set(_message)

    # build the words and words_eol lists
    _words, _words_eol = _split_message(_message)
    words.set(_words)
    words_eol.set(_words_eol)
    # get the user from a WHOIS query

    user.set(User.from_pydle(_bot, sender.get()))
    # determine if we were in a channel
    if _bot.is_channel(target.get()):
        channel.set(target.get())


async def reply(msg: str):
    """
    Sends a message in the same channel or query window as the command was sent.

    Arguments:
        msg (str): Message to send.
    """
    if target.get() is not None:
        await bot.get().message(target.get(), msg)
    else:
        await bot.get().message(user.get().nickname, msg)


def _split_message(string: str) -> Tuple[List[str], List[str]]:
    """
    Split up a string into words and words_eol

    Args:
        string: Any string.

    Returns:
        (list of str, list of str):
            A 2-tuple of (words, words_eol), where words is a list of the words of *string*,
            seperated by whitespace, and words_eol is a list of the same length, with each element
            including the word and everything up to the end of *string*

    Example:
        >>> _split_message("pink fluffy unicorns")
        (['pink', 'fluffy', 'unicorns'], ['pink fluffy unicorns', 'fluffy unicorns', 'unicorns'])
    """
    _words = []
    _words_eol = []
    remaining = string
    while True:
        _words_eol.append(remaining)
        try:
            word, remaining = remaining.split(maxsplit=1)
        except ValueError:
            # we couldn't split -> only one word left
            _words.append(remaining)
            break
        else:
            _words.append(word)

    return _words, _words_eol
