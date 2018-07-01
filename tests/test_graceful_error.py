"""
test_graceful_errors.py - tests for graceful_error module

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
from uuid import UUID

import pytest

from Modules import graceful_errors


@pytest.mark.graceful_error
class TestGracefulErrors(object):
    """
    Tests for the graceful_errors module
    """

    def test_make_graceful(self, monkeypatch):
        ex_id = UUID('faffaec4-18e9-463d-94bd-fad29ff5aa79')
        expected = 'Oh noes! Stinky special_cheese encountered! please contact a tech! Reference code faffaec4'

        # hack CHEESES to only have one item to make test deterministic
        monkeypatch.setattr("Modules.graceful_errors.CHEESES", ["special_cheese"])
        # spawn an instance of a type error
        my_ex = TypeError()  # "Stinky"
        output = graceful_errors.make_graceful(my_ex, ex_id)
        assert expected == output
