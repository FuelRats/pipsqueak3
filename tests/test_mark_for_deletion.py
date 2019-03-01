"""
test_mark_for_deletion.py - tests for MarkForDeletion

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
from typing import Optional
from uuid import uuid4

import pytest

from Modules.mark_for_deletion import MarkForDeletion

pytestmark = pytest.mark.mark_for_deletion

@pytest.mark.parametrize("reason,reporter,marked", [
    ([], 42.2, -1),
    (-2.1, {"Potato"}, None),
    ([], 42, "md reason"),
    (True, -42.2, uuid4())
])
def test_mark_for_deletion_setter_bad_data(reason: str or None, reporter: str or None,
                                           marked: bool, mark_for_deletion_fx: MarkForDeletion):
    """
    Verifies setting the mark for deletion property succeeds only when the data is valid

        Args:
            reason (str): md reason
            reporter(str) md reporter
    """
    with pytest.raises(TypeError):
        mark_for_deletion_fx.reason = reason

    with pytest.raises(TypeError):
        mark_for_deletion_fx.reporter = reporter

    with pytest.raises(TypeError):
        mark_for_deletion_fx.marked = marked

    assert isinstance(mark_for_deletion_fx.marked, bool)
    assert mark_for_deletion_fx.reason != reason
    assert mark_for_deletion_fx.reporter != reporter


@pytest.mark.parametrize("marked,reason,reporter", [(False, None, None),
                                                    (True, "what could possibly go wrong?",
                                                     "cannonFodder"),
                                                    (True, "whats this button do?", "unit_test")])
def test_eq(marked: bool, reason: Optional[str], reporter: Optional[str]):
    md_a = MarkForDeletion(marked, reporter, reason)
    md_b = MarkForDeletion(marked, reporter, reason)
    assert md_a == md_b


@pytest.mark.parametrize("garbage", [None, -1, [], "pft"])
def test_eq_garbage(garbage, mark_for_deletion_fx):
    assert not mark_for_deletion_fx == garbage


@pytest.mark.parametrize("data_a, data_b", [
    ((False, None, None), (True, "smelly", "fart"),),
    ((True, "reason", "unit_test"), (True, "no reason", "unit_test")),
    ((True, "Reasons is say!", "clueless_user"), (True, "Reasons i say!", "helpful_sidewinder99"))
])
def test_ne(data_a, data_b):
    marked_a, reason_a, reporter_a = data_a
    md_a = MarkForDeletion(marked_a, reporter_a, reason_a)

    marked_b, reason_b, reporter_b = data_b
    md_b = MarkForDeletion(marked_b, reporter_b, reason_b)
    assert md_a != md_b


def test_hash_nonzero(mark_for_deletion_fx):
    assert hash(mark_for_deletion_fx) != 0


@pytest.mark.parametrize("alpha, beta", [
    ((False, None, None), (False, None, None)),
    ((True, "Unit_test", "reasons!"), (True, "Unit_test", "reasons!")),
    ((True, "potato", "pft!"), (True, "potato", "pft!")),

])
def test_hash_equal(alpha, beta):
    """ asserts two equal MD objects have the same hash."""

    alpha = MarkForDeletion(*alpha)
    beta = MarkForDeletion(*beta)

    assert hash(alpha) == hash(beta)


@pytest.mark.parametrize("alpha, beta", [
    ((False, None, None), (True, None, None)),
    ((True, "Unit_test", "reasons!"), (True, "potato", "reasons!")),
    ((True, "potato", "uhh..."), (True, "potato", "pft!")),

])
def test_hash_unequal(alpha, beta):
    """asserts two unequal Md objects do not have the same hash."""
    alpha = MarkForDeletion(*alpha)
    beta = MarkForDeletion(*beta)

    assert hash(alpha) != hash(beta)
