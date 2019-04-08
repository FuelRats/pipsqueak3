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
import toml
import logging
import os
import coloredlogs
from typing import Union

from src.packages.cli_manager import cli_manager
from src.config import plugin_manager
config: Union[None, dict] = None


def setup_logging(logfile: str):
    args = cli_manager.args()
    # check for CLI verbosity flag
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    # check for nocolor flag
    if args.nocolors:
        logcolors = False
    else:
        logcolors = True

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
                        isatty=logcolors,
                        )

    # disable propagation
    log.propagate = False

    logging.info("Configuration file loading...")


def setup(filename: str) -> None:
    """
    Sets up the module by loading the specified configuration file from disk

    Args:
        filename (str): path and filename to load.
    """
    global config

    path = f"config/{filename}"
    # check if the file exists
    if os.path.exists(path):
        logging.info(f"Found a file/directory at {filename}'! attempting to load...")
        with open(path, 'r', encoding="UTF8") as infile:
            config_dict = toml.load(infile)
            logging.info("Successfully loaded from file specified!")

        setup_logging(config_dict['logging']['log_file'])
        logging.info("verifying configuration....")
        plugin_manager.hook.validate_config(data=config_dict)  # FIXME: this does nothing as it runs before plugins are loaded
        logging.info("done verifying. config loaded without error.")
        config = config_dict
        logging.info(f"emitting new configuration to plugins...")
        plugin_manager.hook.rehash_handler(data=config_dict)
    else:
        raise FileNotFoundError(f"Unable to find {filename}")


# # fetch the CLI argument
# _path = args().config_file
# # and initialize
# setup(_path)
