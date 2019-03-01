"""
cli_manager.py - Manage CLI arguments

This module will automatically parse arguments provided from the command line when this module is
**first imported** and provide it for importing by other modules via the `args` attribute

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import argparse

# create a new parser
_parser = argparse.ArgumentParser()

# register optional flag for --clean-log, truncating existing log file and starting a new blank one.
_parser.add_argument("--clean-log",
                     help="Start with a clean log file. Deletes any existing log data.",
                     action="store_true")

# register optional argument for the config file
_parser.add_argument("--config-file", "--config", "-c",
                     help="Specify the configuration file to load, relative to config/",
                     default="configuration.json")

# register optional flag for verbose logging
_parser.add_argument("--verbose", "-v",
                     help="Enable verbose logging. Earmuffs sold separately",
                     action="store_true")

# register optional no color flag to remove ANSI coding in logs.
_parser.add_argument("--nocolors", "--nc",
                     help="Disable ANSI color coding. For people who hate fun.",
                     action="store_true")

# parse the arguments into an object
args = _parser.parse_args()
