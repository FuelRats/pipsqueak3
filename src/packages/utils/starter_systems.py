"""
starter_systems.py - Verification function to attempt to detect if the reported system is
    permit-locked to Pilot's Federation and thus requires a starter account to assist

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""


def isStarterSystem(system: str) -> bool:
    """
    Take a system name and attempt to match it to a known list of permit-locked starter systems
    Autocorrecting beyond case normalization is not attempted as all known locked starter systems 
        are not procedurally named
    List of permit-locked starter systems taken from 
        https://elite-dangerous.fandom.com/wiki/Pilots%27_Federation_District 
        and last updated 2020-01-04

    Args:
        system (str): The system name to check

    Returns:
        bool: True if the system name matches a known permit-locked starter system, False otherwise
    """

    listOfStarterSystems = ['AZOTH', 'DROMI', 'LIA FAIL', 'MATET', 'ORNA', 'OTEGINE', 'SHARUR', 
        'TARNKAPPE', 'TYET', 'WOLFSEGEN']

    system = system.upper()

    return system in listOfStarterSystems
