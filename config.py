import json
import logging
import coloredlogs
import os

from typing import Union

CONFIGURATION: Union[None, dict] = None


def setup_logging(root_logger: str, logfile: str):
    log = logging.getLogger(root_logger)
    coloredlogs.install(logger=log,
                        level='debug',
                        isatty=True,
                        datefmt='%y-%m-%d %H:%M:%S',
                        fmt='%(asctime)s [Mecha] %(levelname)s %(message)s',
                        )
    coloredlogs.install(logger=log,
                        level='debug',
                        isatty=False,
                        datefmt='%y-%m-%d %H:%M:%S',
                        fmt='%(asctime)s [Mecha] %(levelname)s %(message)s',
                        handler=logging.FileHandler(logfile, 'a+'),
                        reconfigure=False,
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
