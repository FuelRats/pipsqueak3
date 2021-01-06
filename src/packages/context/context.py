"""
context.py - Command contexts

Provides a context object for use with commands

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from __future__ import annotations  # for forward references standard in >=3.8

import typing
from typing import List, ClassVar

import attr
from loguru import logger

from src.config import CONFIG_MARKER
from ..user import User
from ...config.datamodel import ConfigRoot

if typing.TYPE_CHECKING:
    from src.mechaclient import MechaClient


@CONFIG_MARKER
def validate_config(data: typing.Dict):
    """
    Validate context portion of the configuration file

    Args:
        data(typing.Dict): configuration object
    """
    if not isinstance(data["commands"]["prefix"], str):
        raise ValueError


@CONFIG_MARKER
def rehash_handler(data: ConfigRoot):
    """
    Apply context-related configuration values from event

    Args:
        data(typing.Dict): configuration object
    """
    Context.PREFIX = data.commands.prefix
    Context.DRILL_MODE = data.commands.drill_mode
    logger.debug(f"in rehash handler, using new prefix {Context.PREFIX}")


@attr.dataclass
class Context:
    """
    Command context, stores the context of a command's invocation
    """

    bot: MechaClient
    user: User = attr.ib(validator=attr.validators.instance_of(User))
    target: str = attr.ib(validator=attr.validators.instance_of(str))
    words: List[str] = attr.ib(
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(str),
            iterable_validator=attr.validators.instance_of(list),
        )
    )
    words_eol: List[str] = attr.ib(
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(str),
            iterable_validator=attr.validators.instance_of(list),
        )
    )
    prefixed: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
    PREFIX: ClassVar[str] = "<!!NOTSET!!>"
    DRILL_MODE: ClassVar[bool] = False

    @property
    def channel(self) -> typing.Optional[str]:
        """
        If the message was sent in a channel, this will be its name and `None` otherwise.
        """
        return self.target if self.bot.is_channel(self.target) else None

    @classmethod
    async def from_message(cls, bot: MechaClient, channel: str, sender: str, message: str):
        """
        Creates a context from a IRC message

        Args:
            bot (MechaClient): MechaClient instance
            message (str):  raw message
            sender (str): IRC nickname of the sender
            channel (str): IRC channel the message was sent from

        Returns:
            Context
        """
        # check if the message has our prefix
        prefixed = message.startswith(cls.PREFIX)

        if prefixed:
            # before removing it from the message
            message = message[len(cls.PREFIX):]

        # build the words and words_eol lists
        words, words_eol = _split_message(message)
        # get the user from a WHOIS query
        user = await User.from_pydle(bot, sender)

        # return a built context object
        return cls(bot, user, channel, words, words_eol, prefixed=prefixed)

    async def reply(self, msg: str):
        """
        Sends a message in the same channel or query window as the command was sent.

        Arguments:
            msg (str): Message to send.
        """
        if self.channel is not None:
            await self.bot.message(self.channel, msg)
        else:
            await self.bot.message(self.user.nickname, msg)

    async def replyNotice(self, msg: str):
        """
        Sends a message as a NOTICE to the user that send the command.
        Arguments:
            msg (str): Message to send.
        """
        await self.bot.notice(self.user.nickname, msg)


def _split_message(string: str) -> typing.Tuple[typing.List[str], typing.List[str]]:
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
    # get the words
    words = string.split()

    # reconstruct the original phrase EOL style, through clever usage of slice
    words_eol = [" ".join(words[i:]) for i, _ in enumerate(words)]

    return words, words_eol
