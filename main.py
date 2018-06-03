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
from uuid import uuid4

from Modules import cli_manager, permissions

from pydle import ClientPool, Client

# import config
from Modules.context import Context
from Modules.permissions import require_permission
from Modules.user import User
from config import config
from Modules.rat_command import Commands, CommandNotFoundException

log = logging.getLogger(f"mecha.{__name__}")


class MechaClient(Client):
    """
    MechaSqueak v3
    """

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

    async def on_message(self, channel: str, user: str, message: str):
        """
        Triggered when a message is received
        :param channel: Channel the message arrived in
        :param user: user that triggered the message
        :param message: message body
        :return:
        """
        log.info(f"{channel}: <{user}> {message}")
        if user == config['irc']['nickname']:
            # don't do this and the bot can get into an infinite
            # self-stimulated positive feedback loop.
            log.debug(f"Ignored {message} (anti-loop)")
            return None

        if not message.startswith(Commands.prefix):
            # prevent bot from processing commands without the set prefix
            log.debug(f"Ignored {message} (not a command)")
            return None

        else:  # await command execution

            invoking_user: User = await User.from_bot(bot=self, nickname=user)

            try:
                await Commands.trigger(message=message,
                                       sender=invoking_user,
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
    :param trigger: `Context` object for the command call.
    """
    log.warning(f"cmd_ping triggered on channel '{trigger.channel}' for user "
                f"'{trigger.nickname}'")
    await trigger.reply(f"{trigger.nickname} pong!")


@require_permission(permissions.RAT)
@Commands.command("version", "potato", "ver")
async def cmd_version(bot, trigger: Context):
    """reports mecha's version"""
    await trigger.reply(f"My version is {__version__}")


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
        Commands.bot = CLIENT
        # and run the event loop
        log.info("running forever...")
        pool.handle_forever()
