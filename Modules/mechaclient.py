"""
mechaclient.py - The Pydle Client implementation

This module extends upon the Pydle framework and implements the IRC facing behaviors of Mechasqueak.
this is the IRC client implementation, AKA the MechaClient.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging
from typing import Optional
from uuid import uuid4

from pydle import Client

from Modules import events, graceful_errors
from Modules.context import Context
from Modules.user import User
from config import config
from utils.ratlib import sanitize

log = logging.getLogger(f"mecha.{__name__}")

prefix = config['commands']['prefix']


class MechaClient(Client):
    """
    MechaSqueak v3
    """

    __version__ = "3.0a"

    def __init__(self,
                 *args,
                 handle_errors_gracefully: bool = True,
                 **kwargs):
        """
        Custom mechasqueak constructor

        Unused arguments are passed through to pydle's constructor

        Args:
            *args (list): arguments
            **kwargs (list): keyword arguments
            handle_errors_gracefully(bool): handle raised errors gracefully?

        """
        self._api_handler = None  # TODO: replace with handler init once it exists
        self._database_manager = None  # TODO: replace with dbm once it exists
        self._rat_cache = None  # TODO: replace with ratcache once it exists
        self.graceful_errors = handle_errors_gracefully
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

    async def on_message(self, channel, user, message: str) -> any:
        """
        Triggered when a message is received
        :param channel: Channel the message arrived in
        :param user: user that triggered the message
        :param message: message body
        :return:
        """
        log.debug(f"{channel}: <{user}> {message}")

        try:
            # build a context object
            ctx = await Context.from_message(self, channel, user, message)

            # and emit the raw message
            await events.on_message_raw.emit(context=ctx)

            if ctx.user.nickname.casefold() == self.nickname.casefold():
                # don't do this and the bot can get into an infinite
                # self-stimulated positive feedback loop.
                log.debug(f"Ignored {message} (anti-loop)")
                return None

            if not message.startswith(prefix):
                # prevent bot from processing commands without the set prefix
                log.debug(f"Ignored {message} (not a command)")
                return await events.on_message.emit(context=ctx)

            else:  # await command execution
                # sanitize input string headed to command executor
                sanitized_message = sanitize(message)
                log.debug(f"Sanitized {sanitized_message}, Original: {message}")
                return await events.on_command.emit(context=ctx)

        except Exception as exc:
            ex_uuid = uuid4()
            log.exception(ex_uuid)
            error_message = graceful_errors.make_graceful(exc, ex_uuid)

            # check to see if we are gracefully handling errors
            if self.graceful_errors:
                # and report it to the user
                await self.message(channel, error_message)
            else:
                # we are not handling things gracefully, raise.
                raise exc

    async def on_channel_message(self,
                                 target: str,
                                 sender: str,
                                 message: str):
        """message received in a channel"""

        ctx = await Context.from_message(self,
                                         target,
                                         sender,
                                         message)
        await events.on_channel_message.emit(context=ctx)

    async def on_invite(self, channel: str, sender: str):
        """client invited to a channel"""

        await events.on_invite.emit(channel=channel,
                                    sender=sender,
                                    bot=self)

    async def on_kick(self, channel: str, target: str, sender: str, reason: Optional[str] = None):
        """someone got kicked from a channel"""

        await events.on_kick.emit(channel=channel,
                                  target=target,
                                  sender=sender,
                                  reason=reason,
                                  bot=self)

    async def on_kill(self, target, by, reason):
        """someone got killed"""
        await events.on_kill.emit(target=target,
                                  by=by,
                                  reason=reason,
                                  bot=self)

    async def on_mode_change(self, channel: str, modes, by: str):
        """
        Callback called when the mode on a channel was changed.
        """
        await events.on_mode_change.emit(channel=channel,
                                         modes=modes,
                                         by=by,
                                         bot=self)

    async def on_nick_change(self, old: str, new: str):
        """called when someone changed nicknames"""
        await events.on_nick_change.emit(old=old,
                                         new=new,
                                         bot=self)

    async def on_part(self, channel: str, user: str, reason: Optional[str] = None):
        """called when a user, possibly the client, leaves a channel"""
        await events.on_part.emit(channel=channel,
                                  user=user,
                                  reason=reason,
                                  bot=self)

    async def on_private_message(self, sender: str, message: str):
        """called when the client recieves a direct message"""
        ctx = await Context.from_message(self, self.nickname, sender, message)
        await events.on_private_message.emit(context=ctx)

    async def on_quit(self, user, message=None):
        """called when a user (possibly the client) quits the network"""
        await events.on_quit.emit(user=user,
                                  message=message,
                                  bot=self)

    async def on_topic_change(self, channel: str, topic: str, author: str):
        """called when a channel's topic gets changed"""
        ircUser = await User.from_pydle(self, author)
        await events.on_topic_change.emit(channel=channel,
                                          topic=topic,
                                          user=ircUser,
                                          bot=self)

    async def on_user_mode_change(self, modes):
        """called when the MechaClient's user modes change"""
        await events.on_user_mode_change.emit(modes=modes,
                                              bot=self)

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
