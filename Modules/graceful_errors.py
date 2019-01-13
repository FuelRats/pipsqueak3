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
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Dict
from uuid import UUID, uuid4

from Modules.context import Context
from Modules.rat_board import IndexNotFreeError, RescueBoardException, RescueNotChangedException, \
    RescueNotFoundException

BY_ERROR: Dict[type(Exception), str] = {
    AttributeError: "Overripe",
    IndexError: "Stale",
    TypeError: "Stinky",
    ValueError: "Moldy",
    RuntimeError: "Abominable",
    IndexNotFreeError: "Low-grade",
    RescueBoardException: "Unsavory",
    RescueNotChangedException: "Malodorous",
    RescueNotFoundException: "Repulsive",

}

CHEESES = ['Cheddar', 'Gouda', "Mozzerella", "Asiago", "Monterey Jack", "Brie", "Roquefort", "Edam"]
LOG = getLogger(f"mecha.{__name__}")


@asynccontextmanager
async def graceful(context: Context):
    try:
        yield
    except Exception as exc:
        ex_uuid = uuid4()
        LOG.exception(ex_uuid)
        error_message = make_graceful(exc, ex_uuid)
        # and report it to the user
        await context.bot.message(context.channel, error_message)


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
