"""
rat_command.py - Handles Command registration and Command-triggering IRC events

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

from loguru import logger
from typing import Callable, Any

import psycopg2

from src.packages.rules.rules import get_rule, clear_rules
from ..context import Context
from ..ratmama.ratmama_parser import handle_ratmama_announcement
import pyparsing
from pyparsing import Word, Suppress, Group, alphanums, alphas, ZeroOrMore


# set the logger for rat_command


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
            logger.debug(f"Regular command {ctx.words[0]} invoked.")
        else:
            # Might be a regular rule
            command_fun, extra_args = get_rule(ctx.words, ctx.words_eol, prefixless=False)
            if command_fun:
                logger.debug(
                    f"Rule {getattr(command_fun, '__name__', '')} matching {ctx.words[0]} found.")
            else:
                logger.debug(f"Could not find command or rule for {ctx.words[0]}.")
    else:
        # Might still be a prefixless rule
        command_fun, extra_args = get_rule(ctx.words, ctx.words_eol, prefixless=True)
        if command_fun:
            logger.debug(
                f"Prefixless rule {getattr(command_fun, '__name__', '')} matching {ctx.words[0]} "
                f"found.")

    if ctx.words_eol[0].startswith("Incoming Client:"):
        command_fun = handle_ratmama_announcement

    if command_fun:
        return await command_fun(ctx, *extra_args)

    # neither a rule nor a command, possibly a fact
    result = False
    if ctx.prefixed:
        result = await handle_fact(ctx)
    if not result:
        logger.debug(f"Ignoring message '{ctx.words_eol[0]}'. Not a command or rule.")


async def handle_fact(context: Context):
    """
    Handles potential facts
    """
    logger.trace("entering fact handler")
    pattern = (
            Word(alphanums).setResultsName("name")
            + pyparsing.Optional(Suppress('-') + Word(alphas).setResultsName("lang"))
            + ZeroOrMore(Word(alphanums + '_[]|?.<>{}-=')).setResultsName("subjects")
    )
    logger.debug("parsing {!r} for facts...", context.words_eol[0])
    try:
        result = pattern.parseString(context.words_eol[0])
    except pyparsing.ParseException:
        logger.debug("failed to parse {!r} as a fact", context.words_eol[0])
        return

    fact = result.name
    lang = result.lang if result.lang else 'en'
    users = result.subjects.asList() if result.subjects else []
    try:
        # don't do anything if the fact doesn't exist
        if not await context.bot.fact_manager.exists(fact.casefold(), lang.casefold()):
            logger.debug("no such fact name={!r} lang={!r}", fact, lang)
            return False

        logger.debug("fact exists, retrieving and returning!")
        fact = await context.bot.fact_manager.find(fact.casefold(), lang.casefold())
        await context.reply(f"{' '.join(users)} : {fact.message}")
        return True
    except psycopg2.Error:
        logger.exception("failed to fetch fact")
        return False


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
        logger.debug(f"Registering command aliases: {aliases}...")
        if not _register(func, aliases):
            raise InvalidCommandException("unable to register commands.")
        logger.debug(f"Registration of {aliases} completed.")

        return func

    return real_decorator
