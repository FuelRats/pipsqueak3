"""
Rescue board configuration datamodel

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""


import attr

@attr.dataclass
class BoardConfigRoot:
    cycle_at: int = attr.ib(validator=attr.validators.instance_of(int))
