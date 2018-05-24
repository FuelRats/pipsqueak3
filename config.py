import json
import logging
import coloredlogs
import os

from typing import Union

CONFIGURATION: Union[None, dict] = None


def setup_logging(root_logger: str, logfile: str):
    # hook the logger
    log = logging.getLogger(root_logger)

    # create a handler for said logger...
    file_logger = logging.FileHandler(logfile, 'w')
    log_format = '[%(asctime)s] - [%(levelname)s] - %(message)s'
    file_logger_format = logging.Formatter(log_format)

    # set the formatter to actually use it
    file_logger.setFormatter(file_logger_format)

    # add the handler to the log.
    log.addHandler(file_logger)

    # set proper severity level
    log.setLevel(logging.DEBUG)

    # add Console logging
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logging.getLogger(root_logger).addHandler(console)

    # add console logging format
    console_format = logging.Formatter(log_format)

    # set console formatter to use our format.
    console.setFormatter(console_format)

    # disable propagation
    log.propagate = False

    # Post log current log level
    if log.isEnabledFor(logging.DEBUG):
        log.debug('Logging level set to DEBUG.')
        log.debug('This is a typical level for DEV releases.')


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
