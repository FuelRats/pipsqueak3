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
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional, Type, Union

import attr
import toml
from loguru import logger
import graypy

from src.packages.cli_manager import cli_manager
from ._manager import PLUGIN_MANAGER


@attr.dataclass(frozen=True)
class GelfConfig:
    enabled: bool = attr.ib(validator=attr.validators.instance_of(bool))
    port: Optional[int] = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(int)))
    host: Optional[str] = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(str)))

    log_level: str = attr.ib(default="DEBUG", validator=attr.validators.instance_of(str))
    send_context: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)


def setup_logging(logfile: str, gelf_configuration: Optional[GelfConfig] = None):
    """
    Sets up the logging system

    Args:
        gelf_configuration :
        logfile (str): file path to log into
    """
    args = cli_manager.GET_ARGUMENTS()
    # check for CLI verbosity flag
    if args.trace:
        loglevel = "TRACE"
    elif args.verbose:
        loglevel = "DEBUG"
    else:
        loglevel = "INFO"

    # check for nocolor flag
    if args.nocolors:
        log_colors = False
    else:
        log_colors = True

    # check for new-log flag, overwriting existing log,
    # otherwise, append to the file per normal.
    if args.clean_log:
        log_filemode = "w"
    else:
        log_filemode = "a"

    gelf_data = None
    handlers = [
        dict(
            sink=sys.stdout,
            format="<b><c><{time}</c></b> [{name}] " "<level>{level.name}</level> > {message}",
            colorize=True,
            backtrace=False,
            diagnose=False,
            level=loglevel,
        ),
        dict(
            sink=logfile,
            level="DEBUG",
            format="< {time} > " "[ {module} ] {message}",
            rotation="50 MB",
            enqueue=True,
            mode=log_filemode,
        ),

        dict(
            sink=graypy.GELFTCPHandler(
                "localhost",
                12201,

            ),
            format="<{time}[{name}] {level.name}> {message}",
            colorize=False,
            backtrace=False,
            diagnose=False,
            level=gelf_configuration.log_level,
        )
    ]

    logger.configure(handlers=handlers)

    logger.info("Configuration file loading...")


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
    logger.debug(f"Found a file/directory at {path.resolve(strict=True)}'! attempting to load...")

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

    logger.info(f"Loaded configuration file {path.resolve()} ({checksum})")

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
    gelf_config = GelfConfig(**config_dict["logging"]["gelf"])

    setup_logging(config_dict["logging"]["log_file"], gelf_configuration=gelf_config)
    logger.info(f"new config hash is {file_hash}")
    logger.info("verifying configuration....")

    # NOTE: these members are dynamic, and only exist at runtime. (pylint can't see them.)
    PLUGIN_MANAGER.hook.validate_config(data=config_dict)  # pylint: disable=no-member
    logger.info("done verifying. config loaded without error.")

    logger.info(f"emitting new configuration to plugins...")

    # NOTE: these members are dynamic, and only exist at runtime. (pylint can't see them.)
    PLUGIN_MANAGER.hook.rehash_handler(data=config_dict)  # pylint: disable=no-member
    return config_dict, file_hash
