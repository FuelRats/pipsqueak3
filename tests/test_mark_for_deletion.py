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


@pytest.mark.parametrize("reason,reporter,marked", [
    ([], 42.2, -1),
    (-2.1, {"Potato"}, None),
    ([], 42, "md reason"),
    (True, -42.2, uuid4())
])
def test_mark_for_deletion_setter_bad_data(reason: str or None, reporter: str or None,
                                           marked: bool, mark_for_deletion_fx: MarkForDeletion):
    """
    Verifies setting the mark for deletion property succeeds when the data is valid

        Args:
            rescue_sop_fx (): plain rescue fixture
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
