import typing

import hypothesis
from hypothesis import strategies
from src.packages.rescue import Rescue as _Rescue
from src.packages.rat import Rat as _Rat
from src.packages.utils import sanitize, Platforms as _Platforms
import string

# Anything that isn't a whitespace other than the space character, and isn't a control character.
valid_characters = strategies.characters(blacklist_categories=["C", "Zl", "Zp"])
"""
Any character (ASCII / UNICODE) that isn't a control character or whitespace other than ' '.
"""
# Filtered by anything that doesn't make it through the sanitizer.
valid_text = (
    strategies.text(valid_characters, min_size=10)
        .filter(lambda data: sanitize(data) == data)
        .filter(lambda data: data.isprintable())
)
""" 
Generates probably valid text.

Shrinks towards smaller words.
"""

valid_word_chars = strategies.characters(blacklist_categories=["C", "Z"])
"""
Characters that are valid to be in a word
"""

valid_word = strategies.text(valid_word_chars, min_size=1)
"""
a single word (no whitespace)

Shrinks towards smaller words. 
"""

valid_words = strategies.lists(valid_word, max_size=10)
""" 
a list of valid words

Shrinks towards smaller lists and smaller words.
"""
_irc_nick_letters = strategies.characters(
    whitelist_characters=f"{string.ascii_letters}{string.digits}" + r"\`_[]{}",
    whitelist_categories=())
valid_irc_name = strategies.text(alphabet=_irc_nick_letters, min_size=3).filter(
    lambda word: not word[0].isnumeric())
platform = strategies.sampled_from([_Platforms.PS, _Platforms.PC, _Platforms.XB])
""" Some platform """
rescue = strategies.builds(
    _Rescue,
    uuid=strategies.uuids(version=4),  # generate some valid uuid4
    client=valid_irc_name,  # client should always be defined
    # irc nickname may be any valid word, or None.
    irc_nickname=strategies.one_of(valid_irc_name, strategies.none()),
    platform=platform,
    active=strategies.booleans(),
    code_red=strategies.booleans(),
    board_index=strategies.one_of(strategies.integers(min_value=1), strategies.none())
)
""" Strategy for generating a rescue. Shrinks towards smaller arguments """


def rescues(min_size: int, max_size: int):
    """ builds a list of rescues, shrinks towards smaller lists and smaller rescues """
    return strategies.lists(rescue, min_size=min_size, max_size=max_size,
                            unique_by=(
                                lambda case: case.irc_nickname, lambda case: case.board_index,
                                lambda case: case.client))


""" A list of rescues """

rat = strategies.builds(
    _Rat,
    uuid=strategies.uuids(version=4),
    name=valid_word,
    platforms=strategies.one_of(strategies.none(), platform)
)
""" Generates a valid rat object """

rats = strategies.lists(rat)
""" a list of rats """
