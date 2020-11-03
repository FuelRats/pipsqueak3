#!/usr/bin/env python3
"""
main.py - Mechasqueak3 main program

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import asyncio

from loguru import logger

# noinspection PyUnresolvedReferences
from src import commands  # pylint: disable=unused-import
from src.config import setup
from src.config.datamodel.auth import AuthenticationMethod
from src.mechaclient import MechaClient
from src.packages import cli_manager
# noinspection PyUnresolvedReferences
from src.packages import ratmama  # pylint: disable=unused-import
from src.packages.commands import command
from src.packages.context import Context
from src.packages.permissions import require_permission, RAT

import prometheus_client

TIME_IN_PING = prometheus_client.Summary(
    name="ping",
    documentation="Time spent in the ping command",
    namespace="command",
    unit="seconds"
)


@command("ping", require_permission=RAT)
async def cmd_ping(context: Context):
    """
    Pongs a ping. lets see if the bots alive (command decorator testing)
    :param context: `Context` object for the command call.
    """
    with TIME_IN_PING.time():
        logger.warning(f"cmd_ping triggered on channel '{context.channel}' for user "
                       f"'{context.user.nickname}'")
        await context.reply(f"{context.user.nickname} pong!")


async def start():
    """
    Initializes and connects the client, then passes it to rat_command.
    """

    config, _ = setup(cli_manager.GET_ARGUMENTS().config_file)
    client_args = {"nickname": config.irc.nickname}

    auth_method = config.authentication.method
    if auth_method == AuthenticationMethod.PLAIN:
        client_args["sasl_username"] = config.authentication.plain.username
        client_args["sasl_password"] = config.authentication.plain.password
        client_args["sasl_identity"] = config.authentication.plain.identity
        logger.info("Authenticating via SASL PLAIN.")
    elif auth_method == AuthenticationMethod.EXTERNAL:
        client_args["sasl_mechanism"] = "EXTERNAL"
        cert = config.authentication.external.tls_client_cert
        client_args["tls_client_cert"] = f"certs/{cert}"
        logger.info(f"Authenticating using client certificate at {cert}.")
    elif auth_method == AuthenticationMethod.NO_AUTH:
        ...
    else:
        # this should not be a reachable pathway unless someone didn't use the enum.
        raise ValueError(f"unknown authentication mechanism {auth_method}")

    client = MechaClient(**client_args, mecha_config=config)

    logger.info("connecting to irc...")
    await client.connect(hostname=config.irc.server,
                         port=config.irc.port,
                         tls=config.irc.tls,
                         )

    logger.info("Connected to IRC.")
    if config.telemetry.enabled:
        logger.info("spawning telemetry client w config {}", config.telemetry)
        prometheus_client.start_http_server(
            config.telemetry.bind_port,
            f"{config.telemetry.bind_host}"
        )


# entry point
if __name__ == "__main__":
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(start())
    LOOP.run_forever()
