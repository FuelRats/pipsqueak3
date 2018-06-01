"""
config.py - Configuration facilities

Provides fixtures for loading a configuration from disk.

This modules `setup()` function does not need to be called directly, it will be called
    automatically upon first import.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
import json
import logging
import os
from typing import Union

from Modules import cli_manager  # For CLI config-file argument

config: Union[None, dict] = None


def setup_logging(root_logger: str, logfile: str):
    # create a log formatter
    log_formatter = logging.Formatter("{levelname} [{name}::{funcName}]:{message}",
                                      style='{')
    # get Mecha's root logger
    log = logging.getLogger(root_logger)
    # Create a file handler for the logger
    log_file_handler = logging.FileHandler(logfile, 'w')
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

    logging.info("[Mecha] configuration file loading...")
    """provides facilities for managing a configuration from disk"""


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
        with open(path, 'r') as infile:
            config_dict = json.load(infile)
            logging.info("Successfully loaded JSON from file specified!")

        setup_logging(config_dict["logging"]["base_logger"], config_dict['logging']['log_file'])
        config = config_dict
    else:
        raise FileNotFoundError(f"unable to find {filename}")


# fetch the CLI argument
_path = cli_manager.args.config_file
# and initialize
setup(_path)
