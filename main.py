"""
main.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import logging
# noinspection PyUnresolvedReferences
from Modules import argparsing

from pydle import ClientPool, Client

# import config
from config import config
from Modules.rat_command import Commands

log = logging.getLogger(config["logging"]["base_logger"])


class MechaClient(Client):
    """
    MechaSqueak v3
    """

    version = "3.0a"

    async def on_connect(self):
        """
        Called upon connection to the IRC server
        :return:
        """
        log.debug("on connect invoked")
        # join a channel
        for channel in config["irc"]["channels"]:
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
        log.info(f"trigger! Sender is {user}\t in channel {channel}\twith data"
                 f"{message}")
        if user == config['irc']['nickname']:
            # don't do this and the bot can get into an infinite
            # self-stimulated positive feedback loop.
            log.debug("received message from myself ignoring!.")
            return None

        if not message.startswith(Commands.prefix):
            # prevent bot from processing commands without the set prefix
            log.debug(f"Message {message} did not have our command prefix. Ignoring.")
            return None

        else:  # await command execution
            await Commands.trigger(message=message,
                                   sender=user,
                                   channel=channel)


@Commands.command("ping")
async def cmd_ping(bot, trigger):
    """
    Pongs a ping. lets see if the bots alive (command decorator testing)
    :param bot: Pydle instance.
    :param trigger: `Trigger` object for the command call.
    """
    log.warning(f"cmd_ping triggered on channel '{trigger.channel}' for user "
                f"'{trigger.nickname}'")
    await trigger.reply(f"{trigger.nickname} pong!")

# entry point
if __name__ == "__main__":
    log.info("hello world!")

    pool = ClientPool()
    log.debug("starting bot for server...")
    try:
        log.debug("spawning new bot instance...")
        if config['authentication']['method'] == "PLAIN":
            log.info("Authentication method set to PLAIN.")
            # authenticate via sasl PLAIN mechanism (username & password)
            client = MechaClient(config['irc']['presence'],
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

        log.info(f"connecting to {config['irc']['server']}:{config['irc']['port']}")
        pool.connect(client,
                     config['irc']['server'],
                     config['irc']['port'],
                     tls=config['irc']['tls'])
    except Exception as ex:
        log.error(f"unable to connect to {config['irc']['server']}:"
                  f"{config['irc']['port']}"
                  f"due to an error.")
        log.error(ex)
        raise ex
    else:
        # hand the bot instance to commands
        Commands.bot = client
        # and run the event loop
        log.info("running forever...")
        pool.handle_forever()
