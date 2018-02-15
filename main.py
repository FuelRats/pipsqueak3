"""
main.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from pydle import ClientPool, Client
from Modules.rat_command import Commands
import logging
from config import IRC, Logging

##########
# setup logging stuff

# create a log formatter
log_formatter = logging.Formatter("{levelname} [{name}::{funcName}]:{message}", style='{')
# get Mecha's root logger
log = logging.getLogger(Logging.base_logger)
# Create a file handler for the logger
log_file_handler = logging.FileHandler("logs/MECHASQUEAK.log", 'w')
log_file_handler.setFormatter(log_formatter)
# create a stream handler ( prints to STDOUT/STDERR )
log_stream_handler = logging.StreamHandler()
log_stream_handler.setFormatter(log_formatter)
# adds the two handlers to the logger so they can do their thing.
log.addHandler(log_file_handler)
log.addHandler(log_stream_handler)
# set the minimum severity the logger will report.
# uncomment for production:
# log.setLevel(logging.INFO)
# uncomment for develop:
log.setLevel(logging.DEBUG)

logging.info("[Mecha] Main file loading...")
logging.basicConfig(level=logging.DEBUG)  # write all the things


# end log Setup
####

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
        for channel in IRC.channels:
            await self.join(channel)

        log.debug("joined channels.")
        # call the super
        super().on_connect()
    #
    # def on_join(self, channel, user):
    #     super().on_join(channel, user)

    async def on_message(self, channel, user, message):
        """
        Triggered when a message is received
        :param channel: Channel the message arrived in
        :param user: user that triggered the message
        :param message: message body
        :return:
        """
        log.info(f"trigger! Sender is {user}\t in channel {channel}\twith data {message}")
        if user == IRC.presence:
            # don't do this and the bot can get into an infinite self-stimulated positive feedback loop.
            log.debug("received message from myself ignoring!.")
            return None

        else:  # await command execution
            await Commands.trigger(message=message, sender=user, channel=channel)


@Commands.command("ping")
async def cmd_ping(bot, trigger):
    """
    Pongs a ping. lets see if the bots alive (command decorator testing)
    :param bot: Pydle instance.
    :param trigger: `Trigger` object for the command call.
    """
    # self.message(channel, f"{sender if sender is not None else ''} Potatoes are awesome!")
    log.warning(f"cmd_ping triggered on channel '{trigger.channel}' for user '{trigger.nickname}'")
    await trigger.reply(f"{trigger.nickname} pong!")


# entry point
if __name__ == "__main__":
    log.info("hello world!")

    pool = ClientPool()
    log.debug("starting bot for server...")
    try:
        log.debug("spawning new bot instance...")
        client = MechaClient(IRC.presence)

        log.info(f"connecting to {IRC.server}:{IRC.port}")
        pool.connect(client, IRC.server, IRC.port, tls=IRC.tls)
    except Exception as ex:
        log.error(f"unable to connect to {IRC.server}:{IRC.port} due to an error.")
        log.error(ex)
        from sys import exit
        exit(42)
    else:
        # hand the bot instance to commands
        Commands.bot = client
        # and run the event loop
        log.info("running forever...")
        pool.handle_forever()
