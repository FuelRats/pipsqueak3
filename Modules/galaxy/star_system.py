"""
star_system.py - Handles the creation and parsing of Elite: Dangerous star systems.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from typing import Dict

from dataclasses import dataclass, InitVar

from utils.ratlib import Vector


@dataclass(eq=True, frozen=True)
class StarSystem:
    """
    Dataclass representing a single star system within Elite: Dangerous.
    """

    name: str
    is_populated: bool
    position: Vector
    spectral_class: str = None

    def distance(self, other: 'StarSystem') -> float:
        """
        Finds the distance between this star system and another, in light years.

        Args:
            other (StarSystem): The other star system to measure against.

        Returns:
            A float value indicating the number of light years of distance between the two.
        """
        return self.position.distance(other.position)
