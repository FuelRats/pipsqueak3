from __future__ import annotations

from io import StringIO
from typing import Union, List, Optional

import pytest
from hypothesis import strategies, given

from src.commands import case_management
from src.packages.utils import Platforms
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
    tokens = case_management.CMDR_PATTERN.parseString(payload)
    assert tokens.new_cmdr == subject, "new_cmdr parsed incorrectly."


@given(ident=test_strategies.rescue_identifier())
def test_grab_pattern(ident):
    payload = f"!grab {ident}"
    assert case_management.GRAB_PATTERN.matches(payload), "Unexpected pattern match fail."


@given(ident=test_strategies.rescue_identifier(), new_ident=test_strategies.valid_irc_name())
def test_irc_nick_pattern(ident, new_ident):
    payload = f"!ircnick {ident} {new_ident}"
    tokens = case_management.IRC_NICK_PATTERN.parseString(payload)
    assert tokens.new_nick == new_ident, "new_nick is incorrect."


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
    assert tokens.remainder == remainder_payload, "remainder is incorrect."


@given(ident=test_strategies.rescue_identifier(), remainder=test_strategies.valid_words())
def test_sys_pattern(ident: IDENT_TYPE, remainder: List[str]):
    remainder_payload = " ".join(remainder).strip()
    payload = f"!sys {ident} {remainder_payload}"

    tokens = case_management.SYS_PATTERN.parseString(payload)
    assert tokens.remainder == remainder_payload, "invalid remainder"


@given(
    ident=test_strategies.rescue_identifier(),
    subjects=strategies.lists(test_strategies.valid_irc_name(), min_size=1),
)
def test_unassign_pattern(ident: IDENT_TYPE, subjects: List[str]):
    payload = f"!unassign {ident} {' '.join(subjects)}"
    tokens = case_management.UNASSIGN_PATTERN.parseString(payload)

    assert tokens.rats.asList() == subjects, "Invalid rat list."


@given(
    ident=test_strategies.rescue_identifier(),
    code_red=strategies.one_of(
        strategies.none(),
        strategies.just("cr"),
        strategies.just("code red")
    ),
    timer=strategies.one_of(strategies.none(), test_strategies.timer()),
    remainder=test_strategies.valid_words(),
    platform=strategies.one_of(strategies.none(), test_strategies.platform)
)
def test_inject_pattern(
    ident: IDENT_TYPE, code_red: Optional[str], timer: Optional[str], remainder: List[str], platform: Optional[Platforms]
):
    buffer = StringIO()
    buffer.write(f"!inject {ident} ")
    if platform:
        buffer.write(f"{platform.value} ")

    if code_red:
        buffer.write(f"{code_red} ")
    if timer:
        buffer.write(f"{timer} ")

    for word in remainder:
        buffer.write(f"{word} ")

    buffer.seek(0)
    payload = buffer.read().strip()

    tokens = case_management.INJECT_PATTERN.parseString(payload)
    assert tokens.remainder == " ".join(remainder).strip(), "invalid remainder"

    if code_red:
        assert tokens.code_red == code_red, "code_red failed to parse correctly."

    if timer:
        # produce a list of the elements in the timer
        timer_should_equal = timer.split(':')
        # and re-inject the colon, since its part of the parse group
        timer_should_equal.insert(1, ':')

        # assert equality.
        assert tokens.timer.asList() == timer_should_equal, "timer failed to parse correctly."
