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

from pydle import ClientPool

from Modules import rat_command
from Modules.context import Context
from Modules.mechaclient import MechaClient
from Modules.permissions import require_permission, RAT
from Modules.rat_command import command
from config import config

log = logging.getLogger(f"mecha.{__name__}")


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
