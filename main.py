#!/usr/bin/env python3
"""
main.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import asyncio
import logging
from asyncio import AbstractEventLoop
from uuid import uuid4

from pydle import Client

# noinspection PyUnresolvedReferences
import commands
from Modules.fact_manager import FactManager
from Modules import graceful_errors, rat_command
from Modules.context import Context
from Modules.permissions import require_permission, RAT
from Modules.rat_command import command
from config import config
from utils.ratlib import sanitize

log = logging.getLogger(f"mecha.{__name__}")


class MechaClient(Client):
    """
    MechaSqueak v3
    """

    __version__ = "3.0a"

    def __init__(self, *args, **kwargs):
        """
        Custom mechasqueak constructor

        Unused arguments are passed through to pydle's constructor

        Args:
            *args (list): arguments
            **kwargs (list): keyword arguments

        """
        self._api_handler = None  # TODO: replace with handler init once it exists
        self._fact_manager = None  # Instantiate Global Fact Manager
        self._rat_cache = None  # TODO: replace with ratcache once it exists
        super().__init__(*args, **kwargs)

    async def on_connect(self):
        """
        Called upon connection to the IRC server
        :return:
        """
        log.debug(f"Connecting to channels...")
        # join a channel
        for channel in config["irc"]["channels"]:
            log.debug(f"Configured channel {channel}")
            await self.join(channel)

        log.debug("joined channels.")
        # call the super
        super().on_connect()

    #
    # def on_join(self, channel, user):
    #     super().on_join(channel, user)

    async def on_message(self, channel, user, message: str):
        """
        Triggered when a message is received
        :param channel: Channel the message arrived in
        :param user: user that triggered the message
        :param message: message body
        :return:
        """
        log.debug(f"{channel}: <{user}> {message}")

        if user == config['irc']['nickname']:
            # don't do this and the bot can get int o an infinite
            # self-stimulated positive feedback loop.
            log.debug(f"Ignored {message} (anti-loop)")
            return None
        else:  # await command execution
            # sanitize input string headed to command executor
            sanitized_message = sanitize(message)
            log.debug(f"Sanitized {sanitized_message}, Original: {message}")
            try:
                ctx = await Context.from_message(self, channel, user, sanitized_message)
                await rat_command.trigger(ctx)

            except Exception as ex:
                ex_uuid = uuid4()
                log.exception(ex_uuid)
                error_message = graceful_errors.make_graceful(ex, ex_uuid)
                # and report it to the user
                await self.message(channel, error_message)

    @property
    def rat_cache(self) -> object:
        """
        Mecha's rat cache
        """
        return self._rat_cache

    @property
    def fact_mgr(self) -> FactManager:
        """
        Mecha's fact manager (property)

        This is initialized in a lazy way to increase overall startup speed.
        """
        if not self._fact_manager:
            self._fact_manager = FactManager()  # Instantiate Global Fact Manager
        return self._fact_manager

    @fact_mgr.setter
    def fact_mgr(self, manager: FactManager):
        """
        Mecha's fact manager setter.
        """
        if not isinstance(manager, FactManager):
            raise TypeError("fact_mgr requires a FactManager.")

        log.warning("Fact manager setter invoked!")
        self._fact_manager = manager

    @fact_mgr.deleter
    def fact_mgr(self):
        """
        Mecha's fact manager (deleter)
        """
        log.warning("Fact Manager deleter invoked!")
        del self._fact_manager

    @property
    def api_handler(self) -> object:
        """
        Mecha's API connection
        """
        return self._api_handler


@require_permission(RAT)
@command("ping")
async def cmd_ping(context: Context):
    """
    Pongs a ping. lets see if the bots alive (command decorator testing)
    :param context: `Context` object for the command call.
    """
    log.warning(f"cmd_ping triggered on channel '{context.channel}' for user "
                f"'{context.user.nickname}'")
    await context.reply(f"{context.user.nickname} pong!")


async def start():
    """
    Initializes and connects the client, then passes it to rat_command.
    """
    client_args = {"nickname": config["irc"]["nickname"]}

    auth_method = config["authentication"]["method"]
    if auth_method == "PLAIN":
        client_args["sasl_username"] = config['authentication']['plain']['username']
        client_args["sasl_password"] = config['authentication']['plain']['password']
        client_args["sasl_identity"] = config['authentication']['plain']['identity']
        log.info("Authenticating via SASL PLAIN.")
    elif auth_method == "EXTERNAL":
        client_args["sasl_mechanism"] = "EXTERNAL"
        cert = config['authentication']['external']['tls_client_cert']
        client_args["tls_client_cert"] = f"certs/{cert}"
        log.info(f"Authenticating using client certificate at {cert}.")
    else:
        raise ValueError(f"unknown authentication mechanism {auth_method}")

    client = MechaClient(**client_args)
    await client.connect(hostname=config['irc']['server'],
                         port=config['irc']['port'],
                         tls=config['irc']['tls'],
                         )

    log.info("Connected to IRC.")

# entry point
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
    loop.run_forever()
