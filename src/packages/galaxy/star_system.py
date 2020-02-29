"""
star_system.py - Handles the creation and parsing of Elite: Dangerous star systems.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from dataclasses import dataclass

from src.packages.utils import Vector


@dataclass(eq=True, frozen=True)
class StarSystem:
    """
    Dataclass representing a single star system within Elite: Dangerous.
    """

    name: str
    position: Vector = Vector.zero
    spectral_class: str = None

    def distance(self, other: 'StarSystem') -> float:
        """
        Finds the distance between this star system and another, in light years.

        Args:
            other (StarSystem): The other star system to measure against.

        Returns:
            A float value indicating the number of light years of distance between the two.
        """
        return round(self.position.distance(other.position), 2)
