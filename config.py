import json
import logging
import coloredlogs
import os
import sys
from typing import Union

CONFIGURATION: Union[None, dict] = None


def setup_logging(root_logger: str, logfile: str):
    log_filename = logfile

    logger = logging.getLogger(root_logger)
    logger.setLevel(logging.DEBUG)

    coloredlogs.install(level='debug', isatty=True)

    log_formatter = logging.Formatter('%(asctime)s [Mecha] %(levelname)s : %(message)s')
    log_filehandler = logging.FileHandler(log_filename, 'a+')
    log_filehandler.setLevel(logging.DEBUG)
    log_filehandler.setFormatter(log_formatter)
    logger.addHandler(log_filehandler)

    log_streamhandler = logging.StreamHandler(sys.stdout)
    log_streamhandler.setLevel(logging.DEBUG)
    log_streamhandler.setFormatter(log_formatter)
    logger.addHandler(log_streamhandler)

    # test logging colors:
    logger.debug("DEBUG level message.")
    logger.info("INFO level message.")
    logger.warning("WARN level message.")
    logger.error("ERROR level message.")
    logger.debug("If these messages are colored, then your logs are working.")
    logger.info("configuration file loading...")

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
