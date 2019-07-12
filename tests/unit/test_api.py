"""
test_api.py - tests for the API manager.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""

import asyncio
import logging
import pytest

import aiohttp

from src.packages.utils import Platforms

pytestmark = [pytest.mark.unit, pytest.mark.api]

LOG = logging.getLogger("apitest")


@pytest.mark.asyncio
async def test_find_rat_by_uuid(api_manager_fx):
    """
    Test that we can find a rat via their UUID through the API.
    """
    rat = await api_manager_fx.get_rat(uuid='8dfb8593-4694-44f2-af2f-686b1e6cf48d')


@pytest.mark.asyncio
async def test_find_rat_by_name(api_manager_fx):
    rat = await api_manager_fx.find_rat(name='rat1')


@pytest.mark.asyncio
async def test_find_rat_by_name_and_platform(api_manager_fx):
    rat = await api_manager_fx.find_rat(name='rat1', platform=Platforms.PC)


@pytest.mark.asyncio
async def test_find_rescue_by_uuid(api_manager_fx):
    rescue = await api_manager_fx.get_rescue('4f3a8068-028a-4e0c-9357-947105ec6dc5')
    assert not rescue is None

@pytest.mark.asyncio
async def test_find_rescue_by_uuid_invalid(api_manager_fx):
    rescue = await api_manager_fx.get_rescue('random-uuid')
    assert rescue is None

@pytest.mark.asyncio
async def test_update_rescue(api_manager_fx):
    new_data = {'data': {'IRCNick':'Eearslya2'}}
    #await api_manager_fx.update_rescue('6e9d808d-7d60-4220-ad24-4ababf2a7b29', new_data)


@pytest.mark.asyncio
async def test_create_rescue(api_manager_fx, rescue_sop_fx):
    pass
    #rescue = await api_manager_fx.create_rescue(rescue_sop_fx)
    #breakpoint()


@pytest.mark.asyncio
async def test_rescue_serialize(api_manager_fx, rescue_sop_fx):
    rescue = api_manager_fx._serialize_rescue(rescue_sop_fx)
