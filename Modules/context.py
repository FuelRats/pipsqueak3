"""
context.py - Command contexts

Provides a context object for use with commands

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from typing import Optional

from Modules.User import User
from main import MechaClient


class Context(object):
    """
    Command context, stores the context of a command's invocation
    """

    def __init__(self, user: User, bot: MechaClient, target: str, words: [str], words_eol: [str]):
        """
        Creates a new Commands Context

        Args:
            user (User): invoking IRC user
            bot (MechaClient): Mechaclient instance
            target(str): channel of invoking channel
            words ([str]): list of words from command invocation
            words_eol ([str]): list of words from command invocation to EOL
        """
        self._user: User = user
        self._bot: MechaClient = bot
        self._target: str = target
        self._words: [str] = words
        self._words_eol: [str] = words_eol

    @property
    def user(self) -> User:
        """
        IRC user instance

        Returns:
            User
        """
        return self._user

    @property
    def bot(self) -> MechaClient:
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

    async def reply(self, msg: str):
        """
        Sends a message in the same channel or query window as the command was sent.

        Arguments:
            msg (str): Message to send.
        """
        await self.bot.message(self.channel if self.channel else self.user.nickname, msg)
