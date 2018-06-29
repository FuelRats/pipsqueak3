"""
graceful_errors.py - provides facilities for graceful error handling

Users shouldn't see the actual exception raised from a command invocation,
    rather they should see something more lighthearted and mundane

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from typing import Dict
from uuid import UUID

by_error: Dict[type(Exception), str] = {
    ZeroDivisionError: "Rotten cheddar",
    TypeError: "Bad Tangerines",
}


def make_graceful(ex: Exception, ex_uuid: UUID) -> str:
    """
    makes the incoming exception graceful

    Args:
        ex (Exception): the raised exception to make graceful

    Returns:
        str: graceful error message
    """

    base = "Oh noes! {message} encountered! please contact a tech! Reference code {uuid}"

    ex_type = type(ex)

    # gets the first octet from the uuid
    octet = str(ex_uuid)[:8]

    message = by_error[ex_type] if ex_type in by_error else "unknown error"

    output = base.format(message=message, uuid=octet)

    return output
