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
import logging

# noinspection PyUnresolvedReferences
import commands
from config import config
from mechaclient import MechaClient

log = logging.getLogger(f"mecha.{__name__}")


async def start():
    """
    Initializes and connects the client, then passes it to rat_command.
    """
    client_args = {"nickname": config["irc"]["nickname"]}

    auth_method = config["authentication"]["method"]
    if auth_method == "PLAIN":
        client_args["sasl_username"] = config['authentication']['plain']['username']
        client_args["sasl_password"] = config['authentication']['plain']['password']
        client_args["sasl_identity"] = config['authentication']['plain']['identity']
        log.info("Authenticating via SASL PLAIN.")
    elif auth_method == "EXTERNAL":
        client_args["sasl_mechanism"] = "EXTERNAL"
        cert = config['authentication']['external']['tls_client_cert']
        client_args["tls_client_cert"] = f"certs/{cert}"
        log.info(f"Authenticating using client certificate at {cert}.")
    else:
        raise ValueError(f"unknown authentication mechanism {auth_method}")

    client = MechaClient(**client_args)
    await client.connect(hostname=config['irc']['server'],
                         port=config['irc']['port'],
                         tls=config['irc']['tls'],
                         )

    log.info("Connected to IRC.")


# entry point
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
    loop.run_forever()
