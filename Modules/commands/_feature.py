"""
_feature.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from logging import getLogger
from typing import NoReturn

from pydle import Client

from Modules.context import Context
from Modules.graceful_errors import graceful
from Modules.rules import get_rule
from utils.ratlib import sanitize
from ._registry import Registry

# this isn't a constant, pylint false positive
command_registry = Registry()  # pylint: disable=invalid-name
"""
Commands registry
"""

LOG = getLogger(f"mecha.{__name__}")


class CommandSupport(Client):
    def __init__(self, prefix: str, *args, **kwargs):
        """
        Command Support initializer

        Args:
            prefix (str): prefix for command irc messages
        """
        self.prefix = prefix
        super().__init__(*args, **kwargs)

    async def on_message(self, channel: str, user: str, message: str):
        """
        Commands on_message handler

        Args:
            channel ():
            user ():
            message ():

        Returns:

        """
        LOG.debug(f"{channel}: <{user}> {message}")

        if user.casefold() == self.nickname.casefold():
            # its ourselves. drop it
            LOG.debug("dropping message from self.")
            return

        sanitized_message = sanitize(message)
        LOG.debug(f"Sanitized {sanitized_message}, Original: {message}")

        ctx = await Context.from_message(self, channel, user, sanitized_message)

        async with graceful(ctx):
            if ctx.prefixed:
                await self.on_prefixed_message(ctx)

        await super().on_message(channel, user, message)

    async def on_prefixed_message(self, context: Context) -> NoReturn:
        """
        an incoming message has our commands prefix

        Args:
            context (Context): execution context
        """
        LOG.debug(f"in on_prefixed_message! context={context}")

        cmd = context.words[0].casefold()

        if cmd not in command_registry:
            LOG.debug(f"command {cmd} does not exist / is not known.")

            # emit the event to the superclass
            return await super().on_prefixed_message(context=context)

        LOG.info(f"invoking command {cmd}")
        await command_registry[cmd](context)


class RuleSupport(Client):
    """
    Enables rule-bound  command support.
    """

    async def on_prefixed_message(self, context: Context):
        LOG.debug("in RuleSupport.on_prefixed_message.")
        rule, extra_args = get_rule(context.words, context.words_eol, prefixless=False)
        if rule:
            LOG.debug(
                f"Rule {getattr(rule, '__name__', '')} matching {context.words[0]} found.")

            return await rule(context=context, *extra_args)
        LOG.debug(f"Could not find prefixed rule for {self.prefix}{context.words[0]}.")

    async def on_message(self, channel: str, user: str, message: str):
        context = await Context.from_message(self, channel, user, sanitize(message))
        if context.prefixed:
            return  # discard message, as we are not listening for prefixed rules here.

        command_fun, extra_args = get_rule(context.words, context.words_eol, prefixless=True)
        if command_fun:
            LOG.debug(
                f"Rule {getattr(command_fun, '__name__', '')} matching {context.words[0]} found.")
            async with graceful(context):
                return await command_fun(context=context, *extra_args)
        LOG.debug(f"Could not find prefixless rule for {self.prefix}{context.words[0]}.")
