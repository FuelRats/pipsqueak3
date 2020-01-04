"""
test_autocorrect.py - Tests for the system auto-correction methods.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""

import pytest

from src.packages.utils import isStarterSystem

pytestmark = [pytest.mark.unit, pytest.mark.astarter_systemsutocorrect]

@pytest.mark.parametrize("system_name, expected_outcome", [
    ("Fuelum", False),
    ("sharur", True),
    ("Dromi", True),
    ("COL 285 SECTOR AB-0 85-6", False),
    ("TarnKappe", True)
])
def test_startersystems(system_name, expected_outcome):
    """
    Test that this function correctly identifies permit-locked starter systems.
    """
    assert isStarterSystem(system_name) == expected_outcome
