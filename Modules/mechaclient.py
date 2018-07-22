"""
mechaclient.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging

from pydle import Client

from Modules.event import Event
from config import config
from utils.ratlib import sanitize

log = logging.getLogger(f"mecha.{__name__}")

on_message_raw = Event("on_message_raw")

prefix = config['commands']['prefix']


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
        self._database_manager = None  # TODO: replace with dbm once it exists
        self._rat_cache = None  # TODO: replace with ratcache once it exists
        super().__init__(*args, **kwargs)

    @Event
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
        for subscription in self._subscriptions["on_connect"]:
            log.debug(f"invoking subscription for {subscription}")
            subscription()
        # call the super
        super().on_connect()

    @Event
    async def on_message(self, channel, user, message: str):
        """
        Triggered when a message is received
        :param channel: Channel the message arrived in
        :param user: user that triggered the message
        :param message: message body
        :return:
        """
        log.debug(f"{channel}: <{user}> {message}")
        await on_message_raw(channel, user, message)

        if user == config['irc']['nickname']:
            # don't do this and the bot can get into an infinite
            # self-stimulated positive feedback loop.
            log.debug(f"Ignored {message} (anti-loop)")
            return None

        if not message.startswith(prefix):
            # prevent bot from processing commands without the set prefix
            log.debug(f"Ignored {message} (not a command)")

            return None

        else:  # await command execution
            # sanitize input string headed to command executor
            sanitized_message = sanitize(message)
            log.debug(f"Sanitized {sanitized_message}, Original: {message}")
            await self.on_command(message=sanitized_message, channel=channel, sender=user)

    @Event
    async def on_command(self, message: str, channel: str, sender: str) -> None:
        """
        on_command event
        Args:
            message (str): command's message
            channel (str): command's channel
            sender (str): command's sender

        Returns:
            None
        """
        pass

    @property
    def rat_cache(self) -> object:
        """
        Mecha's rat cache
        """
        return self._rat_cache

    @property
    def database_mgr(self) -> object:
        """
        Mecha's database connection
        """
        return self._database_mgr

    @property
    def api_handler(self) -> object:
        """
        Mecha's API connection
        """
        return self._api_handler
