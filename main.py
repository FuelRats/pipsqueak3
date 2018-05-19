"""
main.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import logging
from uuid import uuid4

from pydle import ClientPool, Client

from Modules import permissions
from Modules.commandcontext import CommandContext
from Modules.permissions import require_permission
from Modules.rat_command import Commands, CommandNotFoundException
from config import IRC, Logging

__version__ = "3.0a"

##########
# setup logging stuff

# create a log formatter
log_formatter = logging.Formatter("{levelname} [{name}::{funcName}]:{message}\t",
                                  style='{')
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
        log.debug(f"trigger! Sender is {user}\t in channel {channel}\twith data"
                  f"{message}")
        if user == IRC.presence:
            # don't do this and the bot can get into an infinite
            # self-stimulated positive feedback loop.
            log.debug("received message from myself ignoring!.")
            return None

        else:  # await command execution
            try:
                await Commands.trigger(message=message,
                                       sender=user,
                                       channel=channel)
            except CommandNotFoundException as ex:
                log.exception(ex)

            except Exception as ex:
                # generate a uuid to attach to the error (to make it easier to find later)
                uuid = uuid4()
                # write a unique marker to the log file for easier searching
                log.error(f"Error during command invocation. marker: {uuid}")
                # write the actual exception, since it may be useful
                log.exception(ex)

                # and report state to the user
                await self.message(channel if channel else user, f"An error has occured during "
                                                                 f"command execution. Please let a "
                                                                 f"techrat  know!"
                                                                 f" -reference id "
                                                                 f"{str(uuid)[:8]}")


@Commands.command("ping")
async def cmd_ping(bot, trigger):
    """
    Pongs a ping. lets see if the bots alive (command decorator testing)
    :param bot: Pydle instance.
    :param trigger: `CommandContext` object for the command call.
    """
    log.warning(f"cmd_ping triggered on channel '{trigger.channel}' for user "
                f"'{trigger.nickname}'")
    await trigger.reply(f"{trigger.nickname} pong!")


@require_permission(permissions.RAT)
@Commands.command("version", "potato", "ver")
async def cmd_version(bot, trigger: CommandContext):
    """reports mecha's version"""
    await trigger.reply(f"My version is {__version__}")


# entry point
if __name__ == "__main__":
    log.info("hello world!")

    pool = ClientPool()
    log.debug("starting bot for server...")
    try:
        log.debug("spawning new bot instance...")
        client = MechaClient(IRC.presence, sasl_username=IRC.Authentication.username,
                             sasl_password=IRC.Authentication.password,
                             sasl_identity='')

        log.info(f"connecting to {IRC.server}:{IRC.port}")
        pool.connect(client, IRC.server, IRC.port, tls=IRC.tls,
                     )
    except Exception as ex:
        log.error(f"unable to connect to {IRC.server}:{IRC.port} "
                  f"due to an error.")
        log.error(ex)
        from sys import exit

        exit(42)
    else:
        # hand the bot instance to commands
        Commands.bot = client
        # and run the event loop
        log.info("running forever...")
        pool.handle_forever()
