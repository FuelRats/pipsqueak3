"""
mechaclient.py - Pydle Client component for mechasqueak3

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from logging import getLogger
from typing import Dict
from uuid import uuid4

from pydle import Client

from config import config
from src.config import implementation_marker
from src.packages.board.rat_board import RatBoard
from src.packages.commands import trigger
from src.packages.context.context import Context
from src.packages.fact_manager.fact_manager import FactManager
from src.packages.graceful_errors import graceful_errors
from src.packages.utils import sanitize

LOG = getLogger(f"mecha.{__name__}")


class MechaClient(Client):
    """
    MechaSqueak v3
    """

    __version__ = "3.0a"

    @implementation_marker
    def validate_config(self, data: Dict):
        print(f"in {self}.validate_config")

    @implementation_marker
    def rehash_handler(self, data: Dict):
        print(f"in {self}.rehash_handler")

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
        self._rat_board = None  # Instantiate Rat Board
        super().__init__(*args, **kwargs)

    async def on_connect(self):
        """
        Called upon connection to the IRC server
        :return:
        """
        LOG.debug(f"Connecting to channels...")
        # join a channel
        for channel in config["irc"]["channels"]:
            LOG.debug(f"Configured channel {channel}")
            await self.join(channel)

        LOG.debug("joined channels.")
        # call the super
        await super().on_connect()

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
        LOG.debug(f"{channel}: <{user}> {message}")

        if user == config['irc']['nickname']:
            # don't do this and the bot can get int o an infinite
            # self-stimulated positive feedback loop.
            LOG.debug(f"Ignored {message} (anti-loop)")
            return None
        # await command execution
        # sanitize input string headed to command executor
        sanitized_message = sanitize(message)
        LOG.debug(f"Sanitized {sanitized_message}, Original: {message}")
        try:
            ctx = await Context.from_message(self, channel, user, sanitized_message)
            await trigger(ctx)

        # Disable pylint's complaint here, as a broad catch is exactly what we want.
        except Exception as ex:  # pylint: disable=broad-except
            ex_uuid = uuid4()
            LOG.exception(ex_uuid)
            error_message = graceful_errors.make_graceful(ex, ex_uuid)
            # and report it to the user
            await self.message(channel, error_message)

    # Vhost Handler
    async def on_raw_396(self, message):
        """
        Handle an IRC 396 message. This message is sent upon successful application of a host mask
        via usermode +x.
        """
        LOG.info(f"{message.params[0]}@{message.params[1]} {message.params[2]}.")

    @property
    def rat_cache(self) -> object:
        """
        Rat Cache
        """
        return self._rat_cache

    @property
    def fact_manager(self) -> FactManager:
        """
        Fact Manager

        This is initialized in a lazy way to increase overall startup speed.
        """
        if not self._fact_manager:
            self._fact_manager = FactManager()  # Instantiate Global Fact Manager
        return self._fact_manager

    @fact_manager.setter
    def fact_manager(self, manager: FactManager):
        """
        Fact Manager Setter.
        """
        if not isinstance(manager, FactManager):
            raise TypeError("fact_manager requires a FactManager.")

        LOG.warning("Fact manager setter invoked!")
        self._fact_manager = manager

    @fact_manager.deleter
    def fact_manager(self):
        """
        Fact Manager Deleter
        """
        LOG.warning("Fact Manager deleter invoked!")
        del self._fact_manager
        self._fact_manager = None

    @property
    def api_handler(self) -> object:
        """
        API Handler property
        """
        return self._api_handler

    @property
    def board(self) -> RatBoard:
        """
        Rat Board property

        """
        if not self._rat_board:
            self._rat_board = RatBoard()  # Create Rat Board Object
        return self._rat_board

    @board.setter
    def board(self, value):
        """
        Rat Board Setter
        """
        if not isinstance(value, RatBoard):
            raise TypeError("board property must be of type RatBoard.")

        LOG.warning("Board Setter invoked!")
        self._rat_board = value

    @board.deleter
    def board(self):
        """
        Rat Board Deleter
        """
        LOG.warning("Board Deleted!")
        del self._rat_board
        self._rat_board = None
