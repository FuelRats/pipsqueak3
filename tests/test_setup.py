"""
test_setup.py

Tests for config.py's setup function.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import pytest
import config


def test_bad_filename(Random_string_fx):
    filename = Random_string_fx
    with pytest.raises(FileNotFoundError):
        config.setup(filename)



