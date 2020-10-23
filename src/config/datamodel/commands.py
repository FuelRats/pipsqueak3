"""
IRC commands configuration datamodel

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""


import attr


@attr.dataclass
class CommandsConfigRoot:
    prefix: str = attr.ib(validator=attr.validators.instance_of(str), default="!")
    drill_mode: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
