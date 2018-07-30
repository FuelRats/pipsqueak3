import logging
import re
from typing import Callable, NamedTuple, Pattern, List, Tuple, Optional

log = logging.getLogger(__name__)

_rules: List["_RuleTuple"] = []
_prefixless_rules: List["_RuleTuple"] = []

_RuleTuple = NamedTuple("_RuleTuple", pattern=Pattern, underlying=Callable, full_message=bool, pass_match=bool)


def rule(regex: str, *, case_sensitive: bool=False, full_message: bool=False,
         pass_match: bool=False, prefixless: bool=False):
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

    Please note that *regex* can match anywhere within the string, it need not match the entire
    string. If you wish to change this behaviour, use '^' and '$' in your regex.
    """
    def decorator(coro: Callable):
        if case_sensitive:
            pattern = re.compile(regex)
        else:
            pattern = re.compile(regex, re.IGNORECASE)

        if prefixless:
            _prefixless_rules.append(_RuleTuple(pattern, coro, full_message, pass_match))
        else:
            _rules.append(_RuleTuple(pattern, coro, full_message, pass_match))

        log.info(f"New rule matching '{regex}' case-{'' if case_sensitive else 'in'}sensitively was"
                 f" created.")
        return coro
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
    for (pattern, fun, full_message, pass_match) in (_prefixless_rules if prefixless else _rules):
        if full_message:
            match = pattern.match(words_eol[0])
        else:
            match = pattern.match(words[0])

        if match is not None:
            if pass_match:
                return fun, (match,)
            else:
                return fun, ()
    else:
        return None, ()


def clear_rules():
    global _prefixless_rules, _rules
    _prefixless_rules = []
    _rules = []
