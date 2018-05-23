import json
import logging
import os
from typing import Union

CONFIGURATION: Union[None, dict] = None


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
    logging.basicConfig(level=logging.DEBUG)  # write all the things

    """provides facilities for managing a configuration from disk"""


def setup(filename: str) -> None:
    """
    Sets up the module by loading the specified configuration file from disk

    Args:
        filename (str): path and filename to load.
    """
    global CONFIGURATION

    path = f"config/{filename}"
    # check if the file exists
    if os.path.exists(path):
        logging.info(f"Found a file/directory at {filename}'! attempting to load...")
        with open(path, 'r') as infile:
            config_dict = json.load(infile)
            logging.info("Successfully loaded JSON from file specified!")

        setup_logging(config_dict["logging"]["base_logger"], config_dict['logging']['log_file'])
        CONFIGURATION = config_dict
    else:
        raise FileNotFoundError(f"unable to find {filename}")
