"""
test_autocorrect.py - Tests for the system auto-correction methods.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""

import pytest

from src.packages.utils import correct_system_name

pytestmark = pytest.mark.autocorrect

@pytest.mark.parametrize("system_name, expected_name", [
    ("Fuelum", "FUELUM"),
    ("COL 285 SECTOR   AB-C   D  5", "COL 285 SECTOR AB-C D5"),
    ("COL 285 SECTOR AB-C D 5-6", "COL 285 SECTOR AB-C D5-6"),
    ("COL 285 SECTOR AB-0 85-6", "COL 285 SECTOR AB-O B5-6"),
    ("COL 285 SECTOR AB-O B5-6", "COL 285 SECTOR AB-O B5-6"),
    ("PRAEA EUQ BN-D B 12-3", "PRAEA EUQ BN-D B12-3"),
    ("SCORPUI SECTOR FB-X A 1-1", "SCORPUI SECTOR FB-X A1-1")
])
def test_correct_system_name(system_name, expected_name):
    """
    Test that this function correctly autocorrects system names.
    """
    assert correct_system_name(system_name) == expected_name
