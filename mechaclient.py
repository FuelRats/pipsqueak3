"""
mechaclient.py - Pydle Client component for mechasqueak3

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from logging import getLogger

import pydle
from pydle import Client

from Modules.commands import CommandSupport, RuleSupport
from Modules.fact_manager import FactManager
from config import config

log = getLogger(f"mecha.{__name__}")


class MechaClientBase(Client):
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
        await super(MechaClientBase, self).on_message(channel, user, message)

        if user == config['irc']['nickname']:
            # don't do this and the bot can get int o an infinite
            # self-stimulated positive feedback loop.
            log.debug(f"Ignored {message} (anti-loop)")
            return None
        # do something

    @property
    def rat_cache(self) -> object:
        """
        Mecha's rat cache
        """
        return self._rat_cache

    @property
    def fact_manager(self) -> FactManager:
        """
        Mecha's fact manager (property)

        This is initialized in a lazy way to increase overall startup speed.
        """
        if not self._fact_manager:
            self._fact_manager = FactManager()  # Instantiate Global Fact Manager
        return self._fact_manager

    @fact_manager.setter
    def fact_manager(self, manager: FactManager):
        """
        Mecha's fact manager setter.
        """
        if not isinstance(manager, FactManager):
            raise TypeError("fact_manager requires a FactManager.")

        log.warning("Fact manager setter invoked!")
        self._fact_manager = manager

    @fact_manager.deleter
    def fact_manager(self):
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


MechaClient = pydle.featurize(MechaClientBase, CommandSupport, RuleSupport)
