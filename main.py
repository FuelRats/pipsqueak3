#!/usr/bin/env python3
"""
main.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import logging
from typing import Dict, List, Callable

from pydle import ClientPool, Client

from Modules import rat_command
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
    SUBSCRIBER_EVENTS = ['on_connect',
                         "on_message",
                         "on_message_RAW",
                         "on_join",
                         "on_command"]
    """Events subscribers can subscribe for
    
    Events:
        on_connect: fired when the MechaClient completes a server connection.
        on_join: fired when the MechaClient joins a channel
        on_message: fired when the MechaClient receives a message NOT from itself.
        on_message_raw: fired when the MechaClient receives any message, **this includes itself!**
        on_command: fired when the MechaClient receives a command invocation
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
        self._subscriptions: Dict[str, List[Callable]] = {
            callback: list() for callback in self.SUBSCRIBER_EVENTS}
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
        for subscription in self._subscriptions["on_connect"]:
            log.debug(f"invoking subscription for {subscription}")
            subscription()
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
        log.debug("on_message invoking on_message_raw subscribers...")

        for subscriber in self._subscriptions['on_message_raw']:
            # call subscribers for the raw on_message event
            logging.debug(f"invoking on_message_raw callback for {subscriber}...")
            subscriber(channel=channel, sender=user, message=message)

        if user == config['irc']['nickname']:
            # don't do this and the bot can get into an infinite
            # self-stimulated positive feedback loop.
            log.debug(f"Ignored {message} (anti-loop)")
            return None

        if not message.startswith(rat_command.prefix):
            # prevent bot from processing commands without the set prefix
            log.debug(f"Ignored {message} (not a command)")

            for subscriber in self._subscriptions['on_message']:
                # call on_message subscriptions
                await subscriber(channel=channel, sender=user, message=message)
            return None

        else:  # await command execution
            # sanitize input string headed to command executor
            sanitized_message = sanitize(message)
            log.debug(f"Sanitized {sanitized_message}, Original: {message}")
            for subscriber in self._subscriptions['on_command']:
                await subscriber(message=sanitized_message, sender=user, channel=channel)
            await rat_command.trigger(message=sanitized_message,
                                      sender=user,
                                      channel=channel)

    def subscribe(self, event: str, callback: Callable):
        """
        Call to subscribe to an Event.
        
        Args:
            event (str): event to subscribe to
            callback (Callable):
        
        Raises:
            ValueError: event not found
        """
        if event not in self._subscriptions:
            raise ValueError(f"'{event}' is not a subscriptable event'")
        else:
            self._subscriptions[event].append(callback)

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


# entry point
if __name__ == "__main__":
    log.info("Initializing...")

    pool = ClientPool()
    log.debug("Starting bot...")
    try:
        log.debug("Spawning instance...")
        if config['authentication']['method'] == "PLAIN":
            log.info("Authentication method set to PLAIN.")
            # authenticate via sasl PLAIN mechanism (username & password)
            client = MechaClient(config['irc']['nickname'],
                                 sasl_username=config['authentication']['plain']['username'],
                                 sasl_password=config['authentication']['plain']['password'],
                                 sasl_identity=config['authentication']['plain']['identity'])

        elif config['authentication']['method'] == "EXTERNAL":
            log.info("Authentication method set to EXTERNAL")
            # authenticate using provided client certificate
            # key and cert may be stored as separate files, as long as mecha can read them.
            cert = config['authentication']['external']['tls_client_cert']
            # key = config['authentication']['external']['tls_client_key']

            client = MechaClient(
                config['irc']['nickname'],
                sasl_mechanism='EXTERNAL',
                tls_client_cert=f"certs/{cert}",
                # tls_client_key=f"certs/{key}"
            )
        else:
            # Pydle doesn't appear to support anything else
            raise TypeError(f"unknown authentication mechanism "
                            f"{config['authentication']['method']}.\n"
                            f"loading cannot continue.")

        log.info(f"Connecting to {config['irc']['server']}:{config['irc']['port']}...")
        pool.connect(client,
                     config['irc']['server'],
                     config['irc']['port'],
                     tls=config['irc']['tls'])
    except Exception as ex:
        log.error(f"Unable to connect to {config['irc']['server']}:"
                  f"{config['irc']['port']}"
                  f"due to an error.")
        log.error(ex)
        raise ex
    else:
        # hand the bot instance to commands
        rat_command.bot = client
        # and run the event loop
        log.info("running forever...")
        pool.handle_forever()
