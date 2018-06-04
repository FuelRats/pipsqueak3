"""
test_user.py - test suite for `Modules.User`

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import pytest

from Modules.User import User


@pytest.mark.parametrize("expected_host", [
    "recruit.fuelrats.com",
    "rat.fuelrats.com",
    "dispatch.fuelrats.com",
    "overseer.fuelrats.com",
    "op.fuelrats.com",
    "techrat.fuelrats.com",
    "netadmin.fuelrats.com",
    "admin.fuelrats.com",
])
@pytest.mark.parametrize("prefix", ["potato.", "Orbital.", ""])
def test_process_vhost(prefix: str, expected_host: str):
    """
    Asserts vhost processing functions as expected
    """
    mixed_host = f"{prefix}{expected_host}"
    assert User.process_vhost(mixed_host) == expected_host


def test_process_vhost_orange():
    """
    Asserts vhost processing works for Orange, as he has a special vhost
    (that can't be tested in the parametrize)
    """
    assert User.process_vhost("i.see.all") == "i.see.all"
