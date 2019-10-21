"""
rules.py
Describes and manages rules that define how IRC commands are triggered.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""


import re
from loguru import logger
from typing import Callable, NamedTuple, Pattern, List, Tuple, Optional


_rules: List["Rule"] = []
_prefixless_rules: List["Rule"] = []


class Rule(NamedTuple):
    """
    Describes a single Rule, which defines a pattern to match to trigger
    an IRC command.
    """

    pattern: Pattern
    underlying: Callable
    full_message: bool
    pass_match: bool

    def __eq__(self, other):
        if isinstance(other, Rule):
            return self.pattern == other.pattern and self.full_message == other.full_message
        return NotImplemented

    def __call__(self, *args, **kwargs):
        return self.underlying(*args, **kwargs)


class RuleNotPresentException(Exception):
    """
    Exception raised when attempting to insert a rule specifically after another rule
    that does not exist.
    """

    def __init__(self, rule_: Rule):
        super().__init__(f"rule matching {rule_.pattern.pattern} does not exist")
        self.rule = rule_


class DuplicateRuleException(Exception):
    """
    Exception raised when attempting to create a rule with the same parameters as
    another already-existing rule.
    """

    def __init__(self, rule_: Rule):
        super().__init__(f"rule matching {rule_.pattern.pattern} is already registered")
        self.rule = rule_


def rule(regex: str, *, case_sensitive: bool = False, full_message: bool = False,
         pass_match: bool = False, prefixless: bool = False, after: Rule = None):
    """
    Decorator to have the underlying coroutine be called when two conditions apply:
    1. No conventional command was found for the incoming message.
    2. The command matches the here provided regular expression.

    Arguments:
        regex (str):
            Regular expression to match the command.
        case_sensitive (bool):
            Whether to match case-sensitively (using the re.IGNORECASE flag).
        full_message (bool):
            If this is True, will try to match against the full message. Otherwise,
            only the word will be matched against.
        pass_match (bool):
            If this is True, the match object will be passed as an argument toward the command
            function.
        prefixless (bool):
            If this is True, the rule can match whether or not the prefix is present. Otherwise, it
            acts similarly to a command, only being considered if the message starts with our
            prefix. The prefix itself should not be part of the regex for non-prefixless rules.
        after (Rule):
            A rule which this one must be considered after, for some rudimentary prioritization.

    Please note that *regex* can match anywhere within the string, it need not match the entire
    string. If you wish to change this behaviour, use '^' and '$' in your regex.

    Ordering is actually ensured by requiring access to *after*, by making sure that it has been
    registered before this one.

    Raises:
        DuplicateRuleException: If the same rule has already been registered.
        RuleNotPresentException: If the rule *after* hasn't yet been registered.
    """

    def decorator(coro: Callable):
        if case_sensitive:
            pattern = re.compile(regex)
        else:
            pattern = re.compile(regex, re.IGNORECASE)

        tuple_ = Rule(pattern, coro, full_message, pass_match)

        target = _prefixless_rules if prefixless else _rules
        if tuple_ in target:
            raise DuplicateRuleException(tuple_)

        if after is None:
            target.append(tuple_)
        else:
            try:
                target.insert(target.index(after) + 1, tuple_)
            except ValueError:
                raise RuleNotPresentException(after)

        logger.info(f"New rule matching '{regex}' "
                    f"case-{'' if case_sensitive else 'in'} sensitively was created.")
        return tuple_

    return decorator


def get_rule(words: List[str], words_eol: List[str],
             prefixless: bool) -> Tuple[Optional[Callable], tuple]:
    """
    Attempt to find a rule in the given dict of patterns and rules.

    Args:
        words: Words of the message.
        words_eol: Words of the message, but each including everything to the end of it.
        prefixless: Whether or not we're looking for prefixless rules.

    Returns:
        (Callable or None, tuple):
            2-tuple of the command function and the extra args that it should
            be called with.
    """
    for rule in _prefixless_rules if prefixless else _rules:
        if rule.full_message:
            match = rule.pattern.match(words_eol[0])
        else:
            match = rule.pattern.match(words[0])

        if match is not None:
            if rule.pass_match:
                return rule.underlying, (match,)

            return rule.underlying, ()

    return None, ()


def clear_rules():
    """
    Removes all previously registered rules.
    """

    _prefixless_rules.clear()
    _rules.clear()
