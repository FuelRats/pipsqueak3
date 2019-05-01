"""
config.py - Configuration facilities

Provides fixtures for loading a configuration from disk.

This modules `setup()` function does not need to be called directly, it will be called
    automatically upon first import.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
import hashlib
import logging
from pathlib import Path
from typing import Dict, Tuple

import coloredlogs
import toml

from src.packages.cli_manager import cli_manager
from ._manager import PLUGIN_MANAGER


def setup_logging(logfile: str):
    """
    Sets up the logging system

    Args:
        logfile (str): file path to log into
    """
    args = cli_manager.GET_ARGUMENTS()
    # check for CLI verbosity flag
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    # check for nocolor flag
    if args.nocolors:
        log_colors = False
    else:
        log_colors = True

    # check for new-log flag, overwriting existing log,
    # otherwise, append to the file per normal.
    if args.clean_log:
        log_filemode = 'w'
    else:
        log_filemode = 'a'

    # hook the logger
    log = logging.getLogger(f"mecha.{__name__}")

    # create a handler for said logger...
    file_logger = logging.FileHandler(logfile, log_filemode, encoding="utf-8")
    log_format = '<%(asctime)s %(name)s> [%(levelname)s] %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    file_logger_format = logging.Formatter(log_format)

    # set the formatter to actually use it
    file_logger.setFormatter(file_logger_format)

    # add the handler to the log.
    logging.getLogger(f"mecha").addHandler(file_logger)

    # set proper severity level
    log.setLevel(loglevel)

    # add Console logging
    console = logging.StreamHandler()
    logging.getLogger(f"mecha.{__name__}").addHandler(console)

    # add console logging format
    console_format = logging.Formatter(log_format)

    # set console formatter to use our format.
    console.setFormatter(console_format)

    # coloredlogs hook
    log_levelstyles = {'critical': {'color': 'red', 'bold': True},
                       'error': {'color': 'red', 'bright': True},
                       'warning': {'color': 'yellow', 'bright': True},
                       'info': {'color': 'white', 'bright': True},
                       'debug': {'color': 'black', 'bright': True}}

    log_fieldstyles = {'asctime': {'color': 'white', 'bright': True},
                       'levelname': {'color': 'white', 'bright': True},
                       'name': {'color': 'yellow', 'bright': True}}

    # coloredlogs hook
    coloredlogs.install(handler=__name__,
                        level=loglevel,
                        fmt=log_format,
                        level_styles=log_levelstyles,
                        field_styles=log_fieldstyles,
                        datefmt=log_datefmt,
                        isatty=log_colors,
                        )

    # disable propagation
    log.propagate = False

    logging.info("Configuration file loading...")


def load_config(filename: str) -> Tuple[Dict, str]:
    """
    Loads the configuration file

    Args:
        filename (str): name of configuration file, relative to ./config

    Returns:
        loaded data and the file's hash.
    """
    path = Path("config") / filename

    # create a new hasher
    hasher = hashlib.sha256()
    # check if the file exists
    logging.debug(f"Found a file/directory at {path.resolve(strict=True)}'! attempting to load...")

    # read the raw bytes into a buffer
    buffer = path.read_bytes()

    # decode buffer so we have the text for toml loading.
    decoded_buffer = buffer.decode("UTF8")

    # update hasher with the raw bytes of the file
    hasher.update(buffer)

    # load the toml
    config_dict = toml.loads(decoded_buffer)
    # digest the file, get its checksum.
    checksum = hasher.hexdigest()

    logging.info(f"Loaded configuration file {path.resolve()} ({checksum})")

    return config_dict, checksum


def setup(filename: str) -> Tuple[Dict, str]:
    """
    Validates and applies the configuration from disk.

    Args:
        filename (str): path and filename to load.

    Returns:
        configuration data located at `filename`.
    """
    # do the loading part
    config_dict, file_hash = load_config(filename)
    setup_logging(config_dict['logging']['log_file'])
    logging.info(f"new config hash is {file_hash}")
    logging.info("verifying configuration....")

    # NOTE: these members are dynamic, and only exist at runtime. (pylint can't see them.)
    PLUGIN_MANAGER.hook.validate_config(  # pylint: disable=no-member
        data=config_dict)
    logging.info("done verifying. config loaded without error.")

    logging.info(f"emitting new configuration to plugins...")

    # NOTE: these members are dynamic, and only exist at runtime. (pylint can't see them.)
    PLUGIN_MANAGER.hook.rehash_handler(data=config_dict)  # pylint: disable=no-member
    return config_dict, file_hash
