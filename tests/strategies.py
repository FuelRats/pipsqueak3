import hypothesis
from hypothesis import strategies
from src.packages.rescue import Rescue as _Rescue
from src.packages.utils import sanitize, Platforms as _Platforms

# Anything that isn't a whitespace other than the space character, and isn't a control character.
valid_characters = strategies.characters(blacklist_categories=["C", "Zl", "Zp"])
# Filtered by anything that doesn't make it through the sanitizer.
valid_text = (
    strategies.text(valid_characters, min_size=10)
        .filter(lambda data: sanitize(data) == data)
        .filter(lambda data: data.isprintable())
)
""" Probably valid generated text """
valid_word_chars = strategies.characters(blacklist_categories=["C", "Z"])
valid_word = strategies.text(valid_word_chars, min_size=1)
""" a single word (no whitespace) """
platforms = strategies.sampled_from([_Platforms.PS, _Platforms.PC, _Platforms.XB])
""" Some platform """

rescues = strategies.builds(
    _Rescue,
    uuid=strategies.uuids(version=4),  # generate some valid uuid4
    client=valid_word,  # client should always be defined
    # irc nickname may be any valid word, or None.
    irc_nickname=strategies.one_of(valid_word, strategies.none()),
    platform=platforms,
    active=strategies.booleans(),
    code_red=strategies.booleans(),
    board_index=strategies.one_of(strategies.integers(min_value=1), strategies.none())
)
""" Strategy for generating rescues """
