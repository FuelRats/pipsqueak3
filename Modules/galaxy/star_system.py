"""
star_system.py - Represents a single star system.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from typing import Dict

from dataclasses import dataclass

from utils.ratlib import Vector


@dataclass(eq=True, frozen=True)
class StarSystem:
    """
    Dataclass representing a single star system within Elite: Dangerous.
    """

    position: Vector
    name: str
    spectral_class: str
    is_populated: bool

    @classmethod
    def from_dict(cls, data: Dict) -> 'StarSystem':
        """
        Takes a Dict of data about a system and parses it out into a proper StarSystem
        object.

        Args:
            data (Dict): A Dict of data containing fields describing a star system.

        Returns:
            An initialized ``StarSystem`` object with the applicable fields in ``data``
            set upon it.
        """

        return cls(Vector(data['x'],
                          data['y'],
                          data['z']),
                   data['name'],
                   data.get('spectral_class'),  # spectral_class may be omitted
                   data['is_populated']
                   )

    def distance(self, other: 'StarSystem') -> float:
        """
        Finds the distance between this star system and another, in light years.

        Args:
            other (StarSystem): The other star system to measure against.

        Returns:
            A float value indicating the number of light years of distance between the two.
        """
        return self.position.distance(other.position)
