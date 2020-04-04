import hypothesis
from hypothesis import strategies

from src.packages.utils import sanitize

# Anything that isn't a whitespace other than the space character, and isn't a control character.
valid_characters = strategies.characters(blacklist_categories=["C", "Zl", "Zp"])
# Filtered by anything that doesn't make it through the sanitizer.
valid_text = strategies.text(valid_characters, min_size=10).filter(lambda data: sanitize(data) == data)
""" Probably valid generated text """
