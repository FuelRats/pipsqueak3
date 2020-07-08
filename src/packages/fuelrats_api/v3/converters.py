from __future__ import annotations

import json
from datetime import datetime
from typing import Union, Any
from uuid import UUID

from dateutil.parser import parse as datetime_parser

from src.packages.utils import Platforms


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


class CustomJsonSerializer(json.JSONEncoder):
    """ custom JSON serializer class because some objects stdlib json throws a fit at. """
    def default(self, o: Any) -> Any:
        if isinstance(o, UUID):
            return f"{o}"
        if isinstance(o, datetime):
            return from_datetime(o)
        return super().default(o)
