from __future__ import annotations
from typing import Union, List
from src.commands import case_management

import pytest
from hypothesis import strategies, given
from .. import strategies as test_strategies

IDENT_TYPE = Union[str, int]

pytestmark = [pytest.mark.unit, pytest.mark.ratsignal_parse, pytest.mark.hypothesis]


@given(
    ident=test_strategies.rescue_identifier(),
    names=strategies.lists(test_strategies.valid_irc_name(), min_size=1),
)
def test_assign_pattern(ident: IDENT_TYPE, names: List[str]):
    """ Verifies the `assign` pattern works """
    payload = f"!assign {ident} {' '.join(names)}"
    assert case_management.ASSIGN_PATTERN.matches(payload), "Unexpected pattern match fail."


@given(
    ident=test_strategies.rescue_identifier(),
)
def test_active_pattern(ident: IDENT_TYPE):
    """ Verifies the `active` pattern works """
    payload = f"!active {ident}"
    assert case_management.ACTIVE_PATTERN.matches(payload), "Unexpected pattern match fail."

