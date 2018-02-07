# coding: utf8
"""
main.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import pydle
from Modules.Handlers import Commands
import logging
from Modules.constants import base_logger

##########
# setup logging stuff

# create a log formatter
log_formatter = logging.Formatter("{levelname} [{name}::{funcName}]:{message}", style='{')
# get Mecha's root logger
log = logging.getLogger(base_logger)
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

class MechaClient(pydle.Client):
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
        await self.join("#unkn0wndev")
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
        log.critical(f"trigger! Sender is {user}\t in channel {channel}\twith data {message}")

        # await command execution
        await Commands.trigger(message=message, sender=user, channel=channel)


@Commands.command("ping")
async def cmd_ping(bot: pydle.Client, channel: str, sender: str):
    """
    Pongs a ping. lets see if the bots alive (command decorator testing)
    :param bot: Pydle instance
    :param channel: text channel the triggering message arrived in
    :param sender: irc name of the invoking user.
    :return:
    """
    # self.message(channel, f"{sender if sender is not None else ''} Potatoes are awesome!")
    log.warning(f"cmd_ping triggered on channel '{channel}' for user '{sender}'")
    await bot.message(channel, f"{sender} pong!")


# entry point
if __name__ == "__main__":
    log.info("hello world!")

    pool = pydle.ClientPool()
    server = "dev.localecho.net"
    log.debug("starting bot for server...")
    try:
        log.debug("spawning new bot instance...")
        client = MechaClient('unknownBot')

        log.info(f"connecting to {server}")
        pool.connect(client, server, tls=False)
    except Exception as ex:
        log.error(f"unable to connect to {server} due to an error.")
        log.error(ex)
        from sys import exit
        exit(42)
    else:
        # hand the bot instance to commands
        Commands.bot = client
        # and run the event loop
        log.info("running forever...")
        pool.handle_forever()
