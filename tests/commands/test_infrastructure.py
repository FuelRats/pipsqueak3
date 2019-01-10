"""
test_infrastructure.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from Modules.commands import command_registry
import pytest
pytestmark = pytest.mark.registry


async def test_command_registration(command_registry_fx):
    @command_registry_fx.register("foo", "bar")
    async def foo(*args, **kwargs):
        ...

    assert "foo" in command_registry
    assert "bar" in command_registry
