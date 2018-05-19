"""
rat_command.py - Handles Command registration and Command-triggering IRC events

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

from functools import wraps
import logging

import re

from pydle import BasicClient

from Modules.trigger import Trigger
import config

# set the logger for handlers

log = logging.getLogger(f'{config.Logging.base_logger}.handlers')


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


class Commands:
    """
    Handles command registration and execution
    """

    # logger facility
    log = logging.getLogger(f"{config.Logging.base_logger}.commands")
    # commands registered with @command will populate this dict
    _registered_commands = {}
    _rules = {}

    # character/s that must prefix a message for it to be parsed as a command.
    prefix = '!'

    # Pydle bot instance.
    bot: BasicClient = None

    @classmethod
    async def trigger(cls, message: str, sender: str, channel: str):
        """
        Invoke a command, passing args and kwargs to the called function
        :param message: triggers message to invoke
        :param sender: author of triggering message
        :param channel: channel of triggering message
        :return: bool command
        """
        if cls.bot is None:
            # someone didn't set me.
            raise CommandException(f"Bot client has not been created or not handed to Commands.")

        # check for trigger
        assert message.startswith(cls.prefix), f"message passed that did not contain prefix."

        cls.log.debug(f"triggered! message is {message}")

        # remove command prefix and make lowercase
        raw_command: str = message.lstrip(cls.prefix).lower()

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

        trigger = Trigger.from_bot_user(cls.bot, sender, channel, words, words_eol)

        if words[0] in cls._registered_commands.keys():
            cmd = cls._registered_commands[words[0]]
        else:
            for key, value in cls._rules.items():
                if key.match(words[0]) is not None:
                    cmd = value
                    break
            else:
                raise CommandNotFoundException(f"Unable to find command {words[0]}")

        return await cmd(cls.bot, trigger)

    @classmethod
    def _register(cls, func, names: list or str) -> bool:
        """
        Register a new command
        :param func: function
        :param names: names to register
        :return: success
        """
        if isinstance(names, str):
            names = [names]  # idiot proofing

        # transform commands to lowercase
        names = [lowered_name.lower() for lowered_name in names]

        if func is None or not callable(func):
            # command not callable
            return False

        else:
            for alias in names:
                if alias in cls._registered_commands:
                    # command already registered
                    raise NameCollisionException(f"attempted to re-register command(s) {alias}")
                else:
                    formed_dict = {alias: func}
                    cls._registered_commands.update(formed_dict)

            return True

    @classmethod
    def _flush(cls)->None:
        """
        Flushes registered commands
        Probably useless outside testing...
        """
        cls._registered_commands = {}
        cls._rules = {}

    @classmethod
    def command(cls, *aliases):
        def real_decorator(func):
            @wraps(func)
            async def wrapper(bot, trigger):
                return await func(bot, trigger)

            # we want to register the wrapper, not the underlying function
            cls.log.debug(f"registering command with aliases: {aliases}...")
            if not cls._register(wrapper, aliases):
                raise InvalidCommandException("unable to register commands.")
            cls.log.debug(f"Success! done registering commands {aliases}!")

            return wrapper
        return real_decorator

    @classmethod
    def rule(cls, regex: str):
        """
        Decorator to have the underlying coroutine be called when two conditions apply:
        1. No conventional command was found for the incoming message.
        2. The command matches the here provided regular expression.

        Arguments:
            regex (str): Regular expression to match the command.
        """
        def decorator(coro):
            async def wrapper(bot, trigger):
                return await coro(bot, trigger)

            cls._rules[re.compile(regex, re.IGNORECASE)] = wrapper
            log.info(f"New rule matching '{regex}' was created.")
            return wrapper
        return decorator
