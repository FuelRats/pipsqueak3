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
from typing import Callable, Dict, Pattern, NamedTuple, Optional, List, Tuple

from pydle import BasicClient

from Modules.context import Context
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
_rules: Dict[Pattern, "_RuleTuple"] = {}
_prefixless_rules: Dict[Pattern, "_RuleTuple"] = {}

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
            command_fun, extra_args = _get_rule(words, words_eol, _rules)
            if command_fun:
                log.debug(f"Rule {getattr(command_fun, '__name__', '')} matching {words[0]} found.")
            else:
                log.warning(f"Could not find command or rule for {prefix}{words[0]}.")
    else:
        # Might still be a prefixless rule
        command_fun, extra_args = _get_rule(words, words_eol, _prefixless_rules)
        if command_fun:
            log.debug(f"Prefixless rule {getattr(command_fun, '__name__', '')} matching {words[0]} "
                      f"found.")

    if command_fun:
        user = await User.from_whois(bot, sender)
        context = Context(bot, user, channel, words, words_eol)
        return await command_fun(context, *extra_args)


def _get_rule(words: List[str], words_eol: List[str],
              from_dict: Dict[Pattern, "_RuleTuple"]) -> Tuple[Optional[Callable], tuple]:
    """
    Attempt to find a rule in the given dict of patterns and rules.

    Args:
        words: Words of the message.
        words_eol: Words of the message, but each including everything to the end of it.
        from_dict: Dict mapping patterns to their rules.

    Returns:
        (Callable or None, tuple):
            2-tuple of the command function and the extra args that it should
            be called with.
    """
    for pattern, (fun, full_message, pass_match) in from_dict.items():
        if full_message:
            match = pattern.match(words_eol[0])
        else:
            match = pattern.match(words[0])

        if match is not None:
            if pass_match:
                return fun, (match,)
            else:
                return fun, ()
    else:
        return None, ()


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
    global _registered_commands, _rules  # again this feels ugly but they are module-level now...
    _registered_commands = {}
    _rules = {}


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


_RuleTuple = NamedTuple("_RuleTuple", underlying=Callable, full_message=bool, pass_match=bool)


def rule(regex: str, *, case_sensitive: bool=False, full_message: bool=False,
         pass_match: bool=False, prefixless: bool=False):
    """
    Decorator to have the underlying coroutine be called when two conditions apply:
    1. No conventional command was found for the incoming message.
    2. The command matches the here provided regular expression.

    Arguments:
        regex (str):
            Regular expression to match the command.
        case_sensitive (bool):
            Whether to match case-sensitively (using the re.IGNORECASE flag).
        full_message (bool):
            If this is True, will try to match against the full message. Otherwise,
            only the word will be matched against.
        pass_match (bool):
            If this is True, the match object will be passed as an argument toward the command
            function.
        prefixless (bool):
            If this is True, the rule can match whether or not the prefix is present. Otherwise, it
            acts similarly to a command, only being considered if the message starts with our
            prefix. The prefix itself should not be part of the regex for non-prefixless rules.

    Please note that *regex* can match anywhere within the string, it need not match the entire
    string. If you wish to change this behaviour, use '^' and '$' in your regex.
    """
    def decorator(coro: Callable):
        if case_sensitive:
            pattern = re.compile(regex)
        else:
            pattern = re.compile(regex, re.IGNORECASE)

        if prefixless:
            _prefixless_rules[pattern] = _RuleTuple(coro, full_message, pass_match)
        else:
            _rules[pattern] = _RuleTuple(coro, full_message, pass_match)

        log.info(f"New rule matching '{regex}' case-{'' if case_sensitive else 'in'}sensitively was"
                 f" created.")
        return coro
    return decorator
