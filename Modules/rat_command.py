"""
rat_command.py - Handles Command registration and Command-triggering IRC events

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import logging
import re
from functools import wraps

from pydle import BasicClient

from Modules.context import Context
from Modules.user import User
from config import config
from Modules.rat_facts import FactsManager

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


class CommandNotFoundException(CommandException):
    """
    Command not found.
    """
    pass


class NameCollisionException(CommandException):
    """
    Someone attempted to register a command already registered.
    """
    pass


_registered_commands = {}
_rules = {}

# character/s that must prefix a message for it to be parsed as a command.
prefix = config['commands']['prefix']

# Pydle bot instance.
bot: BasicClient = None

# facts manager instance
facts_m: FactsManager = FactsManager()


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

    # check for trigger
    assert message.startswith(prefix), f"message passed that did not contain prefix."

    log.debug(f"Trigger! {message}")

    # remove command prefix
    raw_command: str = message.lstrip(prefix)

    words = []
    words_eol = []
    remaining = raw_command
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

        # casts the command to lower case, for case insensitivity
    words[0] = words[0].lower()

    if words[0] in _registered_commands.keys():
        cmd = _registered_commands[words[0]]
    else:
        for key, value in _rules.items():
            if key.match(words[0]) is not None:
                cmd = value
                break
        else:
            cmd = facts_m.handle_fact
            # raise CommandNotFoundException(f"Unable to find command {words[0]}")

    user = await User.from_whois(bot, sender)
    context = Context(bot, user, channel, words, words_eol)
    if cmd == facts_m.handle_fact:
        return_value = await cmd(context)
        if not return_value:
            raise CommandNotFoundException(f"Unable to find command {words[0]}")
    else:
        return await cmd(context)


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
    names = [name.lower() for name in names]

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
    global _registered_commands, _rules  # again this feels ugly but they are module-level now...
    _registered_commands = {}
    _rules = {}


def command(*aliases):
    """
    Registers a command by aliases

    Args:
        *aliases ([str]): aliases to register

    """

    def real_decorator(func):
        """
        The actual commands decorator

        Args:
            func (function): wrapped function

        Returns:
            function
        """

        @wraps(func)
        async def wrapper(context):
            """
            command executor

            Args:
                context: Command IRC context

            Returns:
                whatever the called function returns (probably None)
            """
            return await func(context)

        # we want to register the wrapper, not the underlying function
        log.debug(f"Registering command aliases: {aliases}...")
        if not _register(wrapper, aliases):
            raise InvalidCommandException("unable to register commands.")
        log.debug(f"Registration of {aliases} completed.")

        return wrapper
    return real_decorator


def rule(regex: str):
    """
    Decorator to have the underlying coroutine be called when two conditions apply:
    1. No conventional command was found for the incoming message.
    2. The command matches the here provided regular expression.

    Arguments:
        regex (str): Regular expression to match the command.
    """
    def decorator(coro):
        async def wrapper(context):
            return await coro(context)

        _rules[re.compile(regex, re.IGNORECASE)] = wrapper
        log.info(f"New rule matching '{regex}' was created.")
        return wrapper
    return decorator
