"""
rat_command.py - Handles Command registration and Command-triggering IRC events

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import logging
from typing import Callable, Any, Dict

from src.config import CONFIG_MARKER
from src.packages.rules.rules import get_rule, clear_rules

# set the logger for rat_command
LOG = logging.getLogger(f"mecha.{__name__}")


class CommandException(Exception):
    """
    base Command Exception
    """


class InvalidCommandException(CommandException):
    """
    invoked command failed validation
    """


class NameCollisionException(CommandException):
    """
    Someone attempted to register a command already registered.
    """


_registered_commands = {}  # pylint: disable=invalid-name


@CONFIG_MARKER
def rehash_handler(data: Dict):
    """
    handle rehash events

    Args:
        data (Dict): new config object
    """
    ...  # TODO validation?


@CONFIG_MARKER
def validate_config(data: Dict):
    """
    Validate the configuration file

    Args:
        data (DICT): configuration candidate
    """
    ...  # TODO application?


async def trigger(ctx) -> Any:
    """

    Args:
        ctx (Context): Invocation context

    Returns:
        result of command execution
    """

    if ctx.words_eol[0] == "":
        return  # empty message, bail out

    if ctx.prefixed:
        if ctx.words[0].casefold() in _registered_commands:
            # A regular command
            command_fun = _registered_commands[ctx.words[0].casefold()]
            extra_args = ()
            LOG.debug(f"Regular command {ctx.words[0]} invoked.")
        else:
            # Might be a regular rule
            command_fun, extra_args = get_rule(ctx.words, ctx.words_eol, prefixless=False)
            if command_fun:
                LOG.debug(
                    f"Rule {getattr(command_fun, '__name__', '')} matching {ctx.words[0]} found.")
            else:
                LOG.debug(f"Could not find command or rule for {ctx.words[0]}.")
    else:
        # Might still be a prefixless rule
        command_fun, extra_args = get_rule(ctx.words, ctx.words_eol, prefixless=True)
        if command_fun:
            LOG.debug(
                f"Prefixless rule {getattr(command_fun, '__name__', '')} matching {ctx.words[0]} "
                f"found.")

    if command_fun:
        return await command_fun(ctx, *extra_args)

    LOG.debug(f"Ignoring message '{ctx.words_eol[0]}'. Not a command or rule.")


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

    # again this feels ugly but they are module-level now...
    _registered_commands.clear()
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
        LOG.debug(f"Registering command aliases: {aliases}...")
        if not _register(func, aliases):
            raise InvalidCommandException("unable to register commands.")
        LOG.debug(f"Registration of {aliases} completed.")

        return func

    return real_decorator
