# coding: utf8
"""
config.py - Misc constants

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import logging


class IRC:
    """
    IRC Configuration
    """
    ####
    # Mecha's presence in IRC
    presence = "Mechasqueak3-unknown[BOT]"
    ####
    # Server to connect to
    server = "dev.localecho.net"
    ####
    # Port to connect on
    port = "6667"
    ####
    # use TLS
    tls = False
    ####
    # what channels to connect to
    channels = ["#unkn0wndev"]

    class Authentication:
        """
        Bots Authentication configuration

        Currently this is just a skeleton and has no effect.
        """
        # TODO: Implement SASL authentication
        username = ""
        password = ""
        SASL = True


class Logging:
    """
    Log configurations
    """
    ####
    # Base logger facility, all others are derivatives
    base_logger = 'mecha'
    log_file = f"logs/{IRC.presence}.log"
    verbosity = logging.DEBUG


class Commands:
    ####
    # Mecha's trigger prefix
    trigger = "!"


class RatBoard:
    """
    Configuration options for the RatBoard
    """
    CASE_LIMIT = 30
    """Default limit to board indexies, may be dynamically re-sized during runtime."""
