"""
main.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import logging

from sys import argv

from pydle import ClientPool, Client

import config

# this feels really ugly, im probably going to replace this with argparse or similar.
if len(argv) >= 2:  # assume first argument is the config file to use
    config_filepath = argv[1]
else:  # we didn't get one
    config_filepath = "./config/config.template.json"

print(f"loading configuration from '{config_filepath}'")
config.setup(config_filepath)

from config import CONFIGURATION

from Modules.rat_command import Commands

log = logging.getLogger(CONFIGURATION["logging"]["base_logger"])


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
        log.debug('Connected to IRC Server.')
        # join a channel
        for channel in CONFIGURATION["irc"]["channels"]:
            await self.join(channel)

        log.debug('Successfully joined configured channel.')
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
        log.info(f'Trigger: <{user} {channel}> {message}')
        if user == CONFIGURATION['irc']['presence']:
            # don't do this and the bot can get into an infinite
            # self-stimulated positive feedback loop.
            # log.debug("received message from myself ignoring!.")
            return None

        if not message.startswith(Commands.prefix):
            # prevent bot from processing commands without the set prefix
            log.debug(f'Ignored: {message}')
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
    log.warning(f"Command:  Triggered on channel '{trigger.channel}' for user "
                f"'{trigger.nickname}'")
    await trigger.reply(f"{trigger.nickname} pong!")

# entry point
if __name__ == "__main__":

    pool = ClientPool()
    log.debug("Bot:  Starting bot from pool...")
    try:
        log.debug("Bot:  Spawning new instance...")
        if CONFIGURATION['authentication']['method'] == "PLAIN":
            log.info("Bot:  Authentication method set to PLAIN.")
            # authenticate via sasl PLAIN mechanism (username & password)
            client = MechaClient(CONFIGURATION['irc']['presence'],
                                 sasl_username=CONFIGURATION['authentication']['plain']['username'],
                                 sasl_password=CONFIGURATION['authentication']['plain']['password'],
                                 sasl_identity=CONFIGURATION['authentication']['plain']['identity'])

        elif CONFIGURATION['authentication']['method'] == "EXTERNAL":
            log.info("Bot:  Authentication method set to EXTERNAL")
            # authenticate using provided client certificate
            # key and cert may be stored as separate files, as long as mecha can read them.
            client = MechaClient(
                CONFIGURATION['irc']['presence'],
                sasl_mechanism='EXTERNAL',
                tls_client_cert=f"certs/"
                                f"{CONFIGURATION['authentication']['external']['tls_client_cert']}",
                tls_client_key=f"certs/"
                               f"{CONFIGURATION['authentication']['external']['tls_client_key']}"
            )
        else:
            # Pydle doesn't appear to support anything else
            raise TypeError(f"unknown authentication mechanism "
                            f"{CONFIGURATION['authentication']['method']}.\n"
                            f"loading cannot continue.")

        log.info(f"Bot:  Connecting to {CONFIGURATION['irc']['server']}:{CONFIGURATION['irc']['port']}")
        pool.connect(client,
                     CONFIGURATION['irc']['server'],
                     CONFIGURATION['irc']['port'],
                     tls=CONFIGURATION['irc']['tls'])
    except Exception as ex:
        log.error(f"unable to connect to {CONFIGURATION['irc']['server']}:"
                  f"{CONFIGURATION['irc']['port']}"
                  f"due to an error.")
        log.error(ex)
        raise ex
    else:
        # hand the bot instance to commands
        Commands.bot = client
        # and run the event loop
        log.info("Bot: Wait loop started.")
        pool.handle_forever()
