"""
star_system.py - Represents a single star system.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from dataclasses import dataclass
from typing import Dict

from utils.ratlib import Vector


@dataclass(eq=True, frozen=True)
class StarSystem:
    position: Vector
    name: str
    spectral_class: str
    is_populated: bool

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(Vector(data.get('x'),
                          data.get('y'),
                          data.get('z')),
                   data.get('name'),
                   data.get('spectral_class'),
                   data.get('is_populated')
                   )

    def distance(self, other: 'StarSystem'):
        return self.position.distance(other.position)
