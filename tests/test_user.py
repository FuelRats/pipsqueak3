"""
test_user.py - Test suite for User

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import pytest

from Modules.user import User


@pytest.mark.parametrize("prop", ["target", "realname", "hostname", "nickname", "username", "away",
                                  "account", "identified"])
def test_read_only(user_fx: User, prop: str):
    """ verifies all properties on the User object are read only"""
    # one downside to this approach is new attributes need to be added manually :/
    with pytest.raises(AttributeError):
        user_fx.__setattr__(prop, 42)