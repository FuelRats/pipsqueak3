"""
Parses CLI arguments
"""

import argparse

# create a new parser
_parser = argparse.ArgumentParser()


# add arguments
# - I would wrap this in a list of tuples to be looped over, but each argument may is too specific
# - to enable looping. So we will register them manually.


# register optional argument for the config file
_parser.add_argument("--config-file", "-config", help="Specify the configuration file to load, "
                                                      "relative to config/",
                     default="config.json")
# register optional flag for verbose logging
_parser.add_argument("-verbose", "-v", help="Enable verbose logging. "
                                            "!! caution !! "
                                            "this can be deafening!", action="store_true")
# parse the arguments into an object
args = _parser.parse_args()

# truthy check, as its an optional param
if args.config_file:
    print(f"configuration file set to {args.config_file}")
