"""
test_setup.py

Tests for config.py's setup function.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import pytest
import config

@pytest.mark.setup_tests
def test_bad_filename(random_string_fx):
    """
    Intentionally insert a bad filename to ensure FileNotFoundError
    is thrown, when passed to config.setup.
    """
    filename = random_string_fx
    with pytest.raises(FileNotFoundError):
        config.setup(filename)
