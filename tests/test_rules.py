from typing import Match

import pytest

from Modules.context import Context
from Modules.rat_command import trigger
from Modules.rules import rule, clear_rules, RuleNotPresentException, DuplicateRuleException, \
    get_rule
from tests.mock_callables import AsyncCallableMock, InstanceOf, CallableMock


@pytest.fixture(autouse=True)
def clear_rules_fx():
    clear_rules()


@pytest.mark.asyncio
@pytest.mark.parametrize("regex,case_sensitive,full_message,message", [
    ("^banan(a|e)$", True, False, "!banana"),
    ("^banan(a|e)$", True, False, "!banane"),
    ("^dabadoop$", False, False, "!DABADOOP"),
    ("na na", False, True, "!na na")
])
async def test_rule_matching(async_callable_fx: AsyncCallableMock, regex: str,
                             case_sensitive: bool, full_message: bool, message: str):
    """Verifies that the rule decorator works as expected."""
    rule(regex, case_sensitive=case_sensitive,
         full_message=full_message)(async_callable_fx)

    await trigger(message, "unit_test", "#mordor")
    assert async_callable_fx.was_called_once


@pytest.mark.asyncio
@pytest.mark.parametrize("regex,case_sensitive,full_message,message", [
    ("^banan(a|e)$", True, False, "!banan"),
    ("^banan(a|e)$", True, False, "!bananae"),
    ("^dabadoop$", True, False, "!DABADOOP"),
    ("na na", False, False, "!na na")
])
async def test_rule_not_matching(async_callable_fx: AsyncCallableMock, regex: str,
                                 case_sensitive: bool, full_message: bool, message: str):
    """verifies that the rule decorator works as expected."""
    rule(regex, case_sensitive=case_sensitive,
         full_message=full_message)(async_callable_fx)
    await trigger(message, "unit_test", "theOneWithTheHills")
    assert not async_callable_fx.was_called


@pytest.mark.asyncio
async def test_rule_passes_match(async_callable_fx: AsyncCallableMock):
    """
    Verifies that the rules get passed the match object correctly.
    """
    rule("her(lo)", pass_match=True)(async_callable_fx)
    await trigger("!herlo", "unit_test", "#unit_test")

    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(InstanceOf(Context), InstanceOf(Match))
    assert async_callable_fx.calls[0].args[1].groups() == ("lo",)


@pytest.mark.asyncio
async def test_prefixless_rule_called(async_callable_fx: AsyncCallableMock):
    """
    Verifies that prefixless rules are considered when the prefix is not present.
    """
    rule("da_da(_da)?", prefixless=True)(async_callable_fx)
    await trigger("da_da", "unit_test", "#unit_test")

    assert async_callable_fx.was_called_once
    assert async_callable_fx.was_called_with(InstanceOf(Context))


@pytest.mark.asyncio
@pytest.mark.parametrize("regex,message", [
    ("woof", "!woof woof"),
    ("!woof", "!woof woof")
])
async def test_prefixless_rule_not_called(regex: str, message: str,
                                          async_callable_fx: AsyncCallableMock):
    """
    Verifies that prefixless rules are not considered if the prefix is present.
    """
    rule(regex, prefixless=True)(async_callable_fx)
    await trigger(message, "unit_test", "#unit_test")

    assert not async_callable_fx.was_called


@pytest.mark.asyncio
@pytest.mark.parametrize("regex,full_message,prefixless", [
    ("woof", False, False),
    ("blue moon", True, True),
    ("herlo there", True, False)
])
async def test_rule_duplicate_raises(regex: str, full_message: str, prefixless: str,
                                     async_callable_fx: AsyncCallableMock):
    """
    Ensures that a ValueError is raises when two rules with the same regex, full_message and
    prefixlessness are being registered.
    """
    my_rule = rule(regex, full_message=full_message, prefixless=prefixless)(async_callable_fx)
    with pytest.raises(DuplicateRuleException) as exc_info:
        rule(regex, full_message=full_message, prefixless=prefixless)(async_callable_fx)

    assert exc_info.value.rule is not my_rule
    assert exc_info.value.rule == my_rule


@pytest.mark.asyncio
async def test_rule_not_present_raises(async_callable_fx: AsyncCallableMock):
    """
    Ensures that :class:`RuleNotPresentException` is raised when the provided *after* rule was never
    registered.
    """
    not_present = rule("gaah")(async_callable_fx)
    clear_rules()
    with pytest.raises(RuleNotPresentException) as exc_info:
        rule("baah", after=not_present)(async_callable_fx)

    assert exc_info.value.rule is not_present


@pytest.mark.asyncio
async def test_rule_callable(callable_fx: CallableMock):
    """Ensures that thee result of the rule decorator is still callable."""
    my_rule = rule("gaah")(callable_fx)

    assert callable(my_rule)
    my_rule(1, 2, 3)
    assert callable_fx.was_called_once
    assert callable_fx.was_called_with(1, 2, 3)


@pytest.mark.asyncio
async def test_rule_after():
    """
    Ensures that the *after* parameter behaves as expected.
    This is rather useless as the order in which the rules are registered already ensures their
    order of consideration.
    """
    async_callable_1 = AsyncCallableMock()
    async_callable_2 = AsyncCallableMock()

    rule1 = rule("gaah")(async_callable_1)
    rule2 = rule("(g|b)aah", after=rule1)(async_callable_2)

    await trigger("!gaah", "unit_test", "#channel")
    assert async_callable_1.was_called_once
    assert not async_callable_2.was_called


@pytest.mark.asyncio
@pytest.mark.parametrize("prefixless,pass_match", [
    (False, False),
    (False, True),
    (True, False),
    (True, True)
])
async def test_get_rule(prefixless: bool, pass_match: bool):
    """Ensures that get_rule works as expected."""
    rule1 = rule("gaah", prefixless=prefixless, pass_match=pass_match)(object())
    rule2 = rule("gaah", prefixless=not prefixless)(object())
    rule3 = rule("baah")(object())
    rule4 = rule("baah", prefixless=True)(object())

    fun, extra_args = get_rule(["gaah"], ["gaah"], prefixless)

    assert rule1.underlying is fun
    if pass_match:
        assert 1 == len(extra_args)
        assert isinstance(extra_args[0], Match)
    else:
        assert () == extra_args
