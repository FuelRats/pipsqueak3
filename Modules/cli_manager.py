"""
cli_manager.py - Manage CLI arguments

This module will automatically parse arguments provided from the command line when this module is
**first imported** and provide it for importing by other modules via the `args` attribute

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import argparse
import logging

# create a new parser
_parser = argparse.ArgumentParser()

# add arguments
# - I would wrap this in a list of tuples to be looped over, but each argument may is too specific
# - to enable looping. So we will register them manually.

# register optional flag for --clean-log, truncating existing log file and starting a new blank one.
_parser.add_argument("--clean-log", help="Start with a clean log file.  "
                                         "Deletes any existing log data.",
                     action="store_true")
# register optional argument for the config file
_parser.add_argument("--config-file", "--config", help="Specify the configuration file to load, "
                                                       "relative to config/",
                     default="configuration.json")
# i had to set the above default to testing as pytest refuses to accept CLI args it doesn't
#   expect and there is (apparently) no better solution other than to not give pytest
#   a argument it doesn't expect >.>


# register optional flag for verbose logging
_parser.add_argument("-verbose", "-v", help="Enable verbose logging. "
                                            "Earmuffs sold separately", action="store_true")

# register optional no color flag to remove ANSI coding in logs.
_parser.add_argument("--nocolors", "-nc", help="Disable ANSI color coding. "
                                               "For people who hate fun.", action="store_true")


# parse the *known* arguments into an object
# parse_known_args returns a tuple (Namespace, unknown-args*)
# we only care about the known arguments, thus [0]
args = _parser.parse_known_args()[0]

logging.debug(f"Configuration file set to '{args.config_file}'")
