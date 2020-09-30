from __future__ import annotations

import json
from datetime import datetime
from typing import Union, Any
from uuid import UUID

from dateutil.parser import parse as datetime_parser

from src.packages.utils import Platforms
import cattr

def to_platform(key: str):
    return Platforms[key.upper()]


def to_datetime(raw: Union[str, datetime]) -> datetime:
    """
    convert string to datetime; no-op if the input is already a datetime.

    This method exists because primitive constructors like `int(...)` are idempotent which makes
    them *really useful* for attrs converters. Datetime / `dateutil.parser` is NOT one of these.
    """
    # step 0, if its already a datetime do nothing.
    if isinstance(raw, datetime):
        return raw
    return datetime_parser(raw)


def from_datetime(date: datetime) -> str:
    """
    converts a datetime object back to a ISO string
    """
    return date.isoformat().replace("+00:00", "Z")


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

# Doing this in a loop so both converters get it without duplication...
for converter in (cattr, event_converter):
    # UUID doesn't have a builtin de/structure hook, provide our own
    converter.register_structure_hook(UUID, lambda data, _: UUID(data))
    converter.register_unstructure_hook(UUID, lambda data: f"{data}")
    # Nor does datetime, for some reason
    converter.register_structure_hook(datetime, lambda data, _: to_datetime(data))
    converter.register_unstructure_hook(datetime, lambda date: from_datetime(date))
    # Platforms is an enum so cattr *does* provide one, its just not
    # conformant to the enum in the API so we need our own conversion hook...
    converter.register_structure_hook(Platforms, lambda platform, _: platform.upper())
    converter.register_unstructure_hook(Platforms, lambda platform: platform.value)
