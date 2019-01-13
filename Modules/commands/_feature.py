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
from uuid import uuid4

from pydle import Client

from Modules import graceful_errors
from Modules.context import Context
from utils.ratlib import sanitize
from . import command_registry

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

        if ctx.prefixed:
            await self.on_prefixed(ctx)

    async def on_prefixed(self, context: Context) -> NoReturn:
        """
        an incoming message has our commands prefix

        Args:
            context (Context): execution context
        """
        LOG.debug(f"in on_prefixed! context={context}")

        cmd = context.words[0].casefold()

        if cmd not in command_registry:
            LOG.debug(f"command {cmd} does not exist / is not known.")
            return

        try:
            LOG.info(f"invoking command {cmd}")
            await command_registry[cmd](context)
        except Exception as ex:
            ex_uuid = uuid4()
            LOG.exception(ex_uuid)
            error_message = graceful_errors.make_graceful(ex, ex_uuid)
            # and report it to the user
            await self.message(context.channel, error_message)


@command_registry.register("ping")
async def cmd_ping(context: Context):
    await context.reply("Pong!")
