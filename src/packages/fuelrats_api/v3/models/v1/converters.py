from __future__ import annotations

from datetime import datetime
from typing import Union

from dateutil.parser import parse as datetime_parser

from .....utils import Platforms


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
