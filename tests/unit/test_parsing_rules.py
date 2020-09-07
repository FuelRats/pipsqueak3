from __future__ import annotations
from typing import Union, List, Optional
from src.commands import case_management

import pytest
from loguru import logger
from hypothesis import strategies, given
from .. import strategies as test_strategies

IDENT_TYPE = Union[str, int]

pytestmark = [pytest.mark.unit, pytest.mark.patterns, pytest.mark.hypothesis]


@given(
    ident=test_strategies.rescue_identifier(),
    names=strategies.lists(test_strategies.valid_irc_name(), min_size=1),
)
def test_assign_pattern(ident: IDENT_TYPE, names: List[str]):
    """ Verifies the `assign` pattern works """
    payload = f"!assign {ident} {' '.join(names)}"
    tokens = case_management.ASSIGN_PATTERN.parseString(payload)
    assert tokens.rats.asList() == names, "rat list is incorrect."


@given(
    ident=test_strategies.rescue_identifier(),
)
def test_active_pattern(ident: IDENT_TYPE):
    """ Verifies the `active` pattern works """
    payload = f"!active {ident}"
    assert case_management.ACTIVE_PATTERN.matches(payload), "Unexpected pattern match fail."


@given(
    ident=test_strategies.rescue_identifier(),
    subject=strategies.one_of(test_strategies.valid_irc_name(), strategies.none()),
)
def test_clear_pattern(ident: IDENT_TYPE, subject: Optional[str]):
    payload = f"!clear {ident} {subject if subject else ''}".rstrip()
    tokens = case_management.CLEAR_PATTERN.parseString(payload)
    if subject:
        assert tokens.first_limpet == subject


@given(ident=test_strategies.rescue_identifier(), subject=test_strategies.valid_word())
def test_cmdr_pattern(ident, subject):
    payload = f"!cmdr {ident} {subject}"
    assert case_management.CMDR_PATTERN.matches(payload), "Unexpected pattern match fail."


@given(ident=test_strategies.rescue_identifier())
def test_grab_pattern(ident):
    payload = f"!grab {ident}"
    assert case_management.GRAB_PATTERN.matches(payload), "Unexpected pattern match fail."


@given(ident=test_strategies.rescue_identifier(), new_ident=test_strategies.valid_irc_name())
def test_irc_nick_pattern(ident, new_ident):
    payload = f"!ircnick {ident} {new_ident}"
    assert case_management.IRC_NICK_PATTERN.matches(payload), "Unexpected pattern match fail."


@given(
    ident=test_strategies.rescue_identifier(),
)
def test_just_rescue_pattern(ident):
    payload = f"!ircnick {ident}"
    assert case_management.JUST_RESCUE_PATTERN.matches(payload), "Unexpected pattern match fail."


@given(
    ident=test_strategies.rescue_identifier(),
    index=strategies.integers(min_value=0),
    data=test_strategies.valid_words(min_size=0),
)
def test_sub_cmd_pattern(ident: IDENT_TYPE, index: int, data: List[str]):
    remainder_payload = " ".join(data).strip()
    payload = f"!sub {ident} {index} {remainder_payload}"

    tokens = case_management.SUB_CMD_PATTERN.parseString(payload)

    assert tokens.quote_id == index, "quote_id is incorrect."
    assert tokens.remainder.strip() == remainder_payload, "remainder is incorrect."