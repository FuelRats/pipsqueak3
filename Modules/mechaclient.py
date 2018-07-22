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

from Modules import events
from config import config
from utils.ratlib import sanitize

log = logging.getLogger(f"mecha.{__name__}")

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

        # Event.events['on_connect'].decorated_coro = self.on_connect
        # Event.events['on_message'].decorated_coro = self.on_message
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

        # do event callback
        await events.on_connect.emit(self)
        # call the super
        super().on_connect()

    async def on_message(self, channel, user, message: str):
        """
        Triggered when a message is received
        :param channel: Channel the message arrived in
        :param user: user that triggered the message
        :param message: message body
        :return:
        """
        log.debug(f"{channel}: <{user}> {message}")
        await events.on_message_raw.emit(channel=channel, user=user, message=message)

        if user == config['irc']['nickname']:
            # don't do this and the bot can get into an infinite
            # self-stimulated positive feedback loop.
            log.debug(f"Ignored {message} (anti-loop)")
            return None

        if not message.startswith(prefix):
            # prevent bot from processing commands without the set prefix
            log.debug(f"Ignored {message} (not a command)")
            await events.on_message.emit(channel=channel, user=user, message=message)
            return None

        else:  # await command execution
            # sanitize input string headed to command executor
            sanitized_message = sanitize(message)
            log.debug(f"Sanitized {sanitized_message}, Original: {message}")
            await events.on_command.emit(message=sanitized_message, channel=channel, sender=user)

    async def on_channel_message(self, target, sender, message):
        """message received in a channel"""
        await events.on_channel_message.emit(target, sender, message)

    async def on_channel_notice(self, target, sender, message):
        """notice received in a channel"""
        await events.on_channel_notice.emit(target, sender, message)

    async def on_invite(self, channel, sender):
        """client invited to a channel"""
        await events.on_invite.emit(channel, sender)

    async def on_kick(self, channel, target, sender, reason=None):
        """someone got kicked from a channel"""
        await events.on_kick.emit(channel, target, sender, reason=None)

    async def on_kill(self, target, by, reason):
        """someone got killed"""
        await events.on_kill.emit(target, by, reason)

    async def on_mode_change(self, channel, modes, by):
        """
        Callback called when the mode on a channel was changed.
        """
        await events.on_mode_change.emit(channel, modes, by)

    async def on_nick_change(self, old, new):
        """called when someone changed nicknames"""
        await events.on_nick_change.emit(old, new)

    async def on_notice(self, target, sender, message):
        """someone sent a notice"""
        await events.on_notice.emit(target, sender, message)

    async def on_part(self, channel, user, reason=None):
        """called when a user, possibly the client, leaves a channel"""
        await events.on_part.emit(channel, user, reason=None)

    async def on_private_message(self, sender, message):
        """called when the client recieves a direct message"""
        await events.on_private_message.emit(sender, message)

    async def on_private_notice(self, target, sender, message):
        """called when the client recieves a private notice"""
        await events.on_private_notice.emit(target, sender, message)

    async def on_quit(self, user, message=None):
        """called when a user (possibly the client) quits the network"""
        await events.on_quit.emit(user, message=None)

    async def on_topic_change(self, channel, message, sender):
        """called when a channel's topic gets changed"""
        await events.on_topic_change.emit(channel, message, sender)

    async def on_user_mode_change(self, modes):
        """called when the MechaClient's user modes change"""
        await events.on_user_mode_change.emit(modes)

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
