"""
rat_command.py - Handles Command registration and Command-triggering IRC events

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import logging
from typing import Callable, List, Tuple

from pydle import BasicClient

from Modules.context import Context
from Modules.rules import get_rule, clear_rules
from Modules.user import User
from config import config

# set the logger for rat_command
log = logging.getLogger(f"mecha.{__name__}")


class CommandException(Exception):
    """
    base Command Exception
    """
    pass


class InvalidCommandException(CommandException):
    """
    invoked command failed validation
    """
    pass


class NameCollisionException(CommandException):
    """
    Someone attempted to register a command already registered.
    """
    pass


_registered_commands = {}

# character/s that must prefix a message for it to be parsed as a command.
prefix = config['commands']['prefix']

# Pydle bot instance.
bot: BasicClient = None


async def trigger(message: str, sender: str, channel: str):
    """
    Invoke a command, passing args and kwargs to the called function
    :param message: triggers message to invoke
    :param sender: author of triggering message
    :param channel: channel of triggering message
    :return: bool command
    """
    if bot is None:
        # someone didn't set me.
        raise CommandException(f"Bot client has not been created"
                               f" or not handed to Commands.")
    if message.strip() == "":
        return

    words, words_eol = _split_message(message.lstrip(prefix))
    if message.startswith(prefix):
        if words[0].casefold() in _registered_commands.keys():
            # A regular command
            command_fun = _registered_commands[words[0].casefold()]
            extra_args = ()
            log.debug(f"Regular command {words[0]} invoked.")
        else:
            # Might be a regular rule
            command_fun, extra_args = get_rule(words, words_eol, prefixless=False)
            if command_fun:
                log.debug(f"Rule {getattr(command_fun, '__name__', '')} matching {words[0]} found.")
            else:
                log.warning(f"Could not find command or rule for {prefix}{words[0]}.")
    else:
        # Might still be a prefixless rule
        command_fun, extra_args = get_rule(words, words_eol, prefixless=True)
        if command_fun:
            log.debug(f"Prefixless rule {getattr(command_fun, '__name__', '')} matching {words[0]} "
                      f"found.")

    if command_fun:
        user = await User.from_whois(bot, sender)
        context = Context(bot, user, channel, words, words_eol)
        return await command_fun(context, *extra_args)
    else:
        log.debug(f"Ignoring message '{message}'. Not a command or rule.")


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
    words = []
    words_eol = []
    remaining = string
    while True:
        words_eol.append(remaining)
        try:
            word, remaining = remaining.split(maxsplit=1)
        except ValueError:
            # we couldn't split -> only one word left
            words.append(remaining)
            break
        else:
            words.append(word)

    return words, words_eol


def _register(func, names: list or str) -> bool:
    """
    Register a new command
    :param func: function
    :param names: names to register
    :return: success
    """
    if isinstance(names, str):
        names = [names]  # idiot proofing

    # transform commands to lowercase
    names = [name.casefold() for name in names]

    if func is None or not callable(func):
        # command not callable
        return False

    else:
        for alias in names:
            if alias in _registered_commands:
                # command already registered
                raise NameCollisionException(f"attempted to re-register command(s) {alias}")
            else:
                formed_dict = {alias: func}
                _registered_commands.update(formed_dict)

        return True


def _flush() -> None:
    """
    Flushes registered commands
    Probably useless outside testing...
    """
    global _registered_commands  # again this feels ugly but they are module-level now...
    _registered_commands = {}
    clear_rules()


def command(*aliases):
    """
    Registers a command by aliases

    Args:
        *aliases ([str]): aliases to register

    """

    def real_decorator(func: Callable):
        """
        The actual commands decorator

        Args:
            func (Callable): wrapped function

        Returns:
            Callable: *func*, unmodified.
        """
        log.debug(f"Registering command aliases: {aliases}...")
        if not _register(func, aliases):
            raise InvalidCommandException("unable to register commands.")
        log.debug(f"Registration of {aliases} completed.")

        return func
    return real_decorator
