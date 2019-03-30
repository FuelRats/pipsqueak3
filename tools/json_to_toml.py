"""
json_to_toml.py -   json to toml conversion script

Conversion script for easing the migration from JSON based config files to the new and improved
TOML ones

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import argparse
import json
import pathlib

import toml
from humanfriendly.cli import Spinner


def handle_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("directory", default='.', help="directory to convert")

    return parser.parse_args()


__version__ = (1, 0, 0)

if __name__ == '__main__':
    print(f"""
    =====================================================================
    Json to toml conversion tool version {__version__}.
    
    For rapid conversion of JSON configuration files.
    =====================================================================
    """)
    args = handle_args()
    with Spinner("Setup phase", total=4) as spinner:
        print("verifying path...")
        working_directory = pathlib.Path(args.directory)
        spinner.step()
        print(f"my target path is {working_directory.resolve(strict=True)}")
        spinner.step()
        print(f"looking for files...")
        targets = list(working_directory.glob("*.json"))
        spinner.step()
        if not targets:
            print("Error: no json files detected in directory.  abort.")
            exit(3)
        print(f"found ({len(targets)}) json files to convert.")
        spinner.step()

    with Spinner("Conversion phase", total=len(targets * 2)) as spinner:
        # for each found json
        for json_target in targets:
            # open it for reading
            with json_target.open('r') as ifile:
                # parse it as a json
                data = json.load(ifile)
            spinner.step()
            toml_target = working_directory / f"{json_target.stem}.toml"

            with toml_target.open("w") as ofile:
                toml.dump(data, ofile)

            spinner.step()

    print("all done. have a nice day.")
