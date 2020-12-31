"""
Rescue board configuration datamodel

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""


import attr
import datetime
from datetime import timezone


@attr.dataclass
class BoardConfigRoot:
    cycle_at: int = attr.ib(validator=attr.validators.instance_of(int))
    datetime_last_case: datetime.datetime = attr.ib(validator=attr.validators.instance_of(datetime.datetime), default=datetime.datetime.utcfromtimestamp(0)) # Default to 1900-01-01 00:00
