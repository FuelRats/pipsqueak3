from functools import reduce
from operator import xor
from typing import List, Union

import pydle

from Modules.user import User


class Context(object):
    """
    Object to hold information on the user who invoked a command as well as where and how the
    command was invoked.
    """

    def __init__(self, bot: 'MechaClient', words: List[str], words_eol: List[str], user: User,
                 target: str):
        """
        Initializes a new `Context` object with the provided info.

        Arguments:
            user ():
            bot (pydle.BasicClient): This bot's instance.
            words ([str]): List of all the words of the message which invoked the command. Does not
                include the command prefix char.
            words_eol ([str]): Same as *words* above, but each element including the word and
                everything up to the end of the message.
        """
        self._bot = bot
        self._words = words
        self._words_eol = words_eol
        self._user = user
        self._hash = None
        self._target = target

    bot: 'MechaClient' = property(lambda self: self._bot)
    """MechaClient instance"""
    words: [str] = property(lambda self: self._words)
    words_eol: list = property(lambda self: self._words_eol)
    """words deliminated to EOL"""
    user: User = property(lambda self: self._user)
    """invoking IRC user"""


    @classmethod
    async def from_bot_user(cls, bot: pydle.BasicClient, nickname: str, target: str,
                            words: List[str],
                            words_eol: List[str] = None) -> 'Context':
        """
        Creates a `Trigger` object from a user dictionary as used by pydle.

        Arguments:
            bot (pydle.BasicClient): This bot's instance.
            nickname (str): Command sender's nickname.
            target (str): The message target (usually a channel or, if it was sent in a query
                window, the bot's nick).
            words ([str]): List of all the words of the message which invoked the command. Does not
                include the command prefix char.
            words_eol ([str]): Same as *words* above, but each element including the word and
                everything up to the end of the message.

        Returns:
            Context: Object constructed from the provided info.
        """
        user = await User.from_bot(bot=bot, nickname=nickname)
        return cls(bot, words=words, words_eol=words_eol, user=user, target=target)

    @property
    def channel(self) -> Union[str, None]:
        """
        If the message was sent in a channel, this will be its name and `None` otherwise.
        """
        return self._target if self.bot.is_channel(self._target) else None

    async def reply(self, msg: str):
        """
        Sends a message in the same channel or query window as the command was sent.

        Arguments:
            msg (str): Message to send.
        """
        await self.bot.message(self.channel if self.channel else self.user.username, msg)

    def __eq__(self, other) -> bool:
        if self is other:
            return True
        elif isinstance(other, Context):
            for name, value in Context.__dict__.items():
                if isinstance(value, property):
                    if getattr(self, name) != getattr(other, name):
                        return False
            else:
                return True
        else:
            return False

    def __hash__(self) -> int:
        if self._hash is None:
            attrs = (self._words_eol[0], self.user.identified,
                     self.user.hostname,
                     self.user.realname, self.user.away, self.user.account)
            self._hash = reduce(xor, map(hash, attrs))

        return self._hash
