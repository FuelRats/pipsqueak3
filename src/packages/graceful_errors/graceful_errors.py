"""
graceful_errors.py - provides facilities for graceful error handling

Users shouldn't see the actual exception raised from a command invocation,
    rather they should see something more lighthearted and mundane

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import random
from typing import Dict
from uuid import UUID
from src.packages.fuelrats_api.v3.models.v1.apierror import APIException
BY_ERROR: Dict[type(Exception), str] = {
    AttributeError: "Overripe",
    IndexError: "Stale",
    TypeError: "Stinky",
    ValueError: "Moldy",
    RuntimeError: "Abominable",
    APIException: "Rotten",

}

CHEESES = ['Cheddar', 'Gouda', "Mozzarella", "Asiago", "Monterey Jack", "Brie", "Roquefort", "Edam", "Stilton", "Emmentaler"]


def make_graceful(ex: Exception, ex_uuid: UUID) -> str:
    """
    makes the incoming exception graceful

    Args:
        ex (Exception): the raised exception to make graceful
        ex_uuid(UUID): uuid identifying exception in the logs

    Returns:
        str: graceful error message

    """

    base = "Oh noes! {message} {cheese} encountered! please contact a tech! Reference code {uuid}"

    ex_type = type(ex)

    # gets the first octet from the uuid
    octet = str(ex_uuid)[:8]

    message = BY_ERROR[ex_type] if ex_type in BY_ERROR else "Putrid"

    cheese = random.choice(CHEESES)
    output = base.format(message=message, uuid=octet, cheese=cheese)

    return output
