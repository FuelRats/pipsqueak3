"""
Root IRC presence config datamodel

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""


import attr
from typing import List


@attr.dataclass
class IRCConfigRoot:
    nickname: str = attr.ib(validator=attr.validators.instance_of(str))
    server: str = attr.ib(validator=attr.validators.instance_of(str))
    port: int = attr.ib(validator=attr.validators.instance_of(int))
    tls: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
    channels: List[str] = attr.ib(
        factory=list,
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(str),
            iterable_validator=attr.validators.instance_of(list),
        ),
    )
