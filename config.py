import json
import logging
import coloredlogs
import os
from typing import Union

CONFIGURATION: Union[None, dict] = None


def setup_logging(root_logger: str, logfile: str):
    # create a log formatter
    # log_formatter = logging.Formatter("{levelname} [{name}::{funcName}]:{message}",
    #                                 style='{')
    # get Mecha's root logger
    # log = logging.getLogger(root_logger)
    # Create a file handler for the logger
    # log_file_handler = logging.FileHandler(logfile, 'a+')
    # log_file_handler.setFormatter(log_formatter)
    # create a stream handler ( prints to STDOUT/STDERR )
    # log_stream_handler = logging.StreamHandler()
    # log_stream_handler.setFormatter(log_formatter)
    # adds the two handlers to the logger so they can do their thing.
    # log.addHandler(log_file_handler)
    # log.addHandler(log_stream_handler)

    # hook in coloredlogs, override formatting.
    # NOTE: using manual [Mecha] prefix is no longer required.
    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    coloredlogs.install(level='debug',
                        isatty=True,
                        datefmt='%m-%d %H:%M:%S',
                        fmt='%(asctime)s [Mecha] %(levelname)s %(message)s',
                        reconfigure=True,
                        )

    # test logging colors:
    logging.debug("DEBUG level message.")
    logging.info("INFO level message.")
    logging.warning("WARN level message.")
    logging.error("ERROR level message.")
    logging.debug("If these messages are colored, then your logs are working.")
    logging.info("configuration file loading...")

    """provides facilities for managing a configuration from disk"""


def setup(filename: str) -> None:
    """
    Sets up the module by loading the specified configuration file from disk

    Args:
        filename (str): path and filename to load.
    """
    global CONFIGURATION

    # check if the file exists
    if os.path.exists(filename):
        logging.info(f"Found a file with name '{filename}'! attempting to load...")
        with open(filename, 'r') as infile:
            config_dict = json.load(infile)
            logging.info("Successfully loaded JSON from file specified!")

        setup_logging(config_dict["logging"]["base_logger"], config_dict['logging']['log_file'])
        CONFIGURATION = config_dict
    else:
        raise FileNotFoundError(f"unable to find {filename}")
