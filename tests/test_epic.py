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
def test_constructor(rat_good_fx: Rats, uuid: UUID, rescue_plain_fx, random_string_fx: str):
    epic = Epic(uuid, random_string_fx, rescue_plain_fx, rat_good_fx)

    assert uuid == epic.uuid
    assert rescue_plain_fx == epic.rescue
    assert rat_good_fx == epic.rat
    assert random_string_fx == epic.notes


def test_eq(epic_fx: Epic):
    assert epic_fx == epic_fx


def test_ne(epic_fx: Epic):
    other = Epic(uuid4(), "potato express")
    assert epic_fx != other
    # as Epic is nullable, this (bad) equality check is necessary
    assert None != epic_fx


def test_hash(epic_fx: Epic):
    epic_hash = hash(epic_fx)
    assert epic_hash != 0
