import json
import logging
import coloredlogs
import os
import sys
from typing import Union

CONFIGURATION: Union[None, dict] = None


def setup_logging(root_logger: str, logfile: str):
    log_level = logging.DEBUG
    log_filename = logfile

    logger = logging.getLogger(root_logger)
    logger.setLevel(log_level)

    coloredlogs.install(logger, isatty=True)

    log_formatter = logging.Formatter('%(asctime)s [Mecha]%(levelname)s : %(message)s')
    log_filehandler = logging.FileHandler(log_filename, 'a+')
    log_filehandler.setLevel(log_level)
    log_filehandler.setFormatter(log_formatter)
    logger.addHandler(log_filehandler)

    log_streamhandler = logging.StreamHandler(sys.stdout)
    log_streamhandler.setLevel(log_level)
    log_streamhandler.setFormatter(log_formatter)
    logger.addHandler(log_streamhandler)





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
