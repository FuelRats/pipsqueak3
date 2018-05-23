import json
import logging
import coloredlogs
import os
import sys
from typing import Union

CONFIGURATION: Union[None, dict] = None


def setup_logging(root_logger: str, logfile: str):
    log_filename = logfile

    log = logging.getLogger(root_logger)
    log.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter('%(asctime)s [Mecha] %(levelname)s : %(message)s')
    log_filehandler = logging.FileHandler(log_filename, 'a+')
    log_filehandler.setLevel(logging.DEBUG)
    log_filehandler.setFormatter(log_formatter)
    log.addHandler(log_filehandler)

    log_streamhandler = logging.StreamHandler(sys.stdout)
    log_streamhandler.setLevel(logging.DEBUG)
    log_streamhandler.setFormatter(log_formatter)
    log.addHandler(log_streamhandler)

    # test logging colors:
    log.debug("DEBUG level message.")
    log.info("INFO level message.")
    log.warning("WARN level message.")
    log.error("ERROR level message.")
    log.debug("If these messages are colored, then your logs are working.")
    log.info("configuration file loading...")

    coloredlogs.install(level='debug',
                        isatty=True,
                        logger=log,
                        fmt='%(asctime)s [Mecha] %(levelname)s : %(message)s'
                        )



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
