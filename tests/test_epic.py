"""
test_epic.py

Tests for the epic module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from uuid import UUID, uuid4

import pytest

from Modules.epic import Epic
from Modules.rats import Rats


@pytest.mark.parametrize("uuid", (uuid4(), uuid4(), uuid4()))
def test_constructor(RatGood_fx: Rats, uuid: UUID, RescuePlain_fx, Random_string_fx: str):
    epic = Epic(uuid, Random_string_fx, RescuePlain_fx, RatGood_fx)

    assert uuid == epic.uuid
    assert RescuePlain_fx == epic.rescue
    assert RatGood_fx == epic.rat
    assert Random_string_fx == epic.notes
