from __future__ import annotations

import json

import pendulum
from pendulum import DateTime
from typing import Union, Any
from uuid import UUID

from loguru import logger

from src.packages.utils import Platforms
import cattr


def to_platform(key: str):
    return Platforms[key.upper()]


def to_datetime(raw: Union[str, DateTime]) -> DateTime:
    """
    convert string to DateTime; no-op if the input is already a DateTime.

    This method exists because primitive constructors like `int(...)` are idempotent which makes
    them *really useful* for attrs converters. Datetime / `dateutil.parser` is NOT one of these.
    """
    # step 0, if its already a DateTime do nothing.
    if isinstance(raw, DateTime):
        return raw
    return pendulum.parse(raw)


def from_datetime(date: pendulum.DateTime) -> str:
    """
    converts a DateTime object back to a ISO string
    """
    return date.astimezone(pendulum.tz.UTC).isoformat().replace("+00:00", "Z")


def to_uuid(raw: Union[str, UUID]) -> UUID:
    """ idempotent UUID constructor """
    if not isinstance(raw, UUID):
        return UUID(raw)
    return raw


event_converter = cattr.Converter(unstruct_strat=cattr.UnstructureStrategy.AS_TUPLE)
"""
event structure converter.

Events come in effectively as a tuple, which doesn't match the default `cattr` global converter,
thus we need to define a second one that uses tuples instead.

(Either that or a magically complicated dict comprehension that isn't very performant.)
"""


def structure_uuid(data: str, *args) -> UUID:
    logger.debug(f"structuring {data} as uuid...")
    return UUID(data)


# Doing this in a loop so both converters get it without duplication...
for converter in (cattr, event_converter):
    # UUID doesn't have a builtin de/structure hook, provide our own
    converter.register_structure_hook(UUID, structure_uuid)
    converter.register_unstructure_hook(UUID, lambda data: f"{data}")
    converter.register_structure_hook(DateTime, lambda data, _: to_datetime(data))
    converter.register_unstructure_hook(DateTime, lambda date: from_datetime(date))
    # Platforms is an enum so cattr *does* provide one, its just not
    # conformant to the enum in the API so we need our own conversion hook...
    converter.register_structure_hook(Platforms, lambda platform, _: Platforms[platform.upper()])
    converter.register_unstructure_hook(Platforms, lambda platform: platform.value.casefold())
