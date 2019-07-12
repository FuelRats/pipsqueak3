"""
test_api.py - tests for the API manager.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""

import logging
from uuid import UUID
import pytest

from src.packages.utils import Platforms, Status

pytestmark = [pytest.mark.unit, pytest.mark.api]  # pylint: disable=invalid-name

LOG = logging.getLogger("apitest")


@pytest.mark.asyncio
async def test_find_rat_by_uuid(api_manager_fx):
    """
    Test that we can find a rat via their UUID through the API.
    """
    rat = await api_manager_fx.get_rat(uuid='8dfb8593-4694-44f2-af2f-686b1e6cf48d')
    assert rat is not None
    assert rat.uuid == UUID('8dfb8593-4694-44f2-af2f-686b1e6cf48d')
    assert rat.name == 'rat1'
    assert rat.platform == Platforms.PC


@pytest.mark.asyncio
async def test_find_rat_by_name(api_manager_fx):
    """
    Test that we can find a rat via their name.
    """
    rat = await api_manager_fx.find_rat(name='rat1')
    assert rat is not None
    assert rat.uuid == UUID('8dfb8593-4694-44f2-af2f-686b1e6cf48d')
    assert rat.name == 'rat1'
    assert rat.platform == Platforms.PC


@pytest.mark.asyncio
async def test_find_rat_by_name_and_platform(api_manager_fx):
    """
    Test that we can find a rat by both name and platform.
    """
    rat = await api_manager_fx.find_rat(name='rat1', platform=Platforms.PC)
    assert rat is not None
    assert rat.uuid == UUID('8dfb8593-4694-44f2-af2f-686b1e6cf48d')
    assert rat.name == 'rat1'
    assert rat.platform == Platforms.PC


@pytest.mark.asyncio
async def test_find_rescue_by_uuid(api_manager_fx):
    """
    Test that we can find a rescue by its UUID.
    """
    rescue = await api_manager_fx.get_rescue('26560069-ff2f-485d-bd11-8cb878b570c0')
    assert rescue is not None
    assert rescue.status == Status.OPEN
    assert rescue.rats
    assert rescue.rats[0].name == 'rat1'


@pytest.mark.asyncio
async def test_find_rescue_by_uuid_invalid(api_manager_fx):
    """
    Test that trying to find a rescue that doesn't exist returns None.
    """
    rescue = await api_manager_fx.get_rescue('random-uuid')
    assert rescue is None


@pytest.mark.skip(reason='WIP')
@pytest.mark.asyncio
async def test_create_rescue(api_manager_fx, rescue_sop_fx):
    """
    Test that we can create a rescue in the API.
    """
    rescue = await api_manager_fx.create_rescue(rescue_sop_fx)
    assert rescue.client == rescue_sop_fx.client
    assert rescue.platform == rescue_sop_fx.platform
    assert rescue.system == rescue_sop_fx.system


@pytest.mark.skip(reason='WIP')
@pytest.mark.asyncio
async def test_update_rescue(api_manager_fx, rescue_sop_fx):
    """
    Test that we can perform a full update of a rescue in the API.
    """
    await api_manager_fx.update_rescue(rescue_sop_fx)


@pytest.mark.asyncio
async def test_rescue_serialize(api_manager_fx, rescue_sop_fx):
    """
    Assert that we can serialize a Rescue object into a properly-formatted Dict.
    """
    rescue = api_manager_fx._serialize_rescue(rescue_sop_fx)  # pylint: disable=protected-access
    assert rescue
    assert rescue['attributes']
