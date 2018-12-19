"""
context.py - Command contexts

Provides a context object for use with commands

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

prefix = config['commands']['prefix']


class Context(object):
    """
    Command context, stores the context of a command's invocation
    """

    def __init__(self, bot: 'MechaClient',
                 user: User,
                 target: str,
                 words: [str],
                 words_eol: [str],
                 prefixed: bool = False
                 ):
        """
        Creates a new Commands Context

        Args:
            user (User): invoking IRC user
            bot (MechaClient): Mechaclient instance
            target(str): channel of invoking channel
            words ([str]): list of words from command invocation
            words_eol ([str]): list of words from command invocation to EOL
            prefixed (bool): marker if the message is prefixed
        """
        self._user: User = user
        self._bot: 'MechaClient' = bot
        self._target: str = target
        self._words: [str] = words
        self._words_eol: [str] = words_eol
        self._prefixed: bool = prefixed

    @property
    def prefixed(self):
        """
        Flag marking if the created context is a command/prefixed invocation
        Returns:

        """
        return self._prefixed

    @property
    def user(self) -> User:
        """
        IRC user instance

        Returns:
            User
        """
        return self._user

    @property
    def bot(self) -> 'MechaClient':
        """
        MechaClient instance

        Returns:
            MechaClient
        """
        return self._bot

    @property
    def words(self) -> [str]:
        """
        words in invoking message

        Returns:
            list[str]: list of words
        """
        return self._words

    @property
    def words_eol(self) -> [str]:
        """
        Words in invoking message to EOL

        Returns:
            list[str]
        """
        return self._words_eol

    @property
    def target(self) -> str:
        """
        Target of command invocation

        Returns:
            str
        """
        return self._target

    @property
    def channel(self) -> Optional[str]:
        """
        If the message was sent in a channel, this will be its name and `None` otherwise.
        """
        return self.target if self.bot.is_channel(self.target) else None


def from_message():
    """
    Populates the context from a IRC message
    """
    _message = message.get()
    _bot = bot.get()
    # check if the message has our prefix
    _prefixed = _message.startswith(prefix)

    if _prefixed:
        prefixed.set(_message.startswith(prefix))
        # before removing it from the message
        _message = _message[len(prefix):]
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
