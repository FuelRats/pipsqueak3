"""
test_rat_cache.py - tests the rat_cache

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from uuid import uuid4

import pytest

from src.packages.rat.rat import Rat
from src.packages.cache.rat_cache import RatCache
from src.packages.utils import Platforms

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_find_rat_by_name_existing(rat_good_fx: Rat, rat_cache_fx):
    """
    Verifies that cached rats can be found by name
    """
    found_rat = await rat_cache_fx.get_rat_by_name(name=rat_good_fx.name)
    assert rat_good_fx == found_rat


@pytest.mark.parametrize("actual, invalids", [
    (Platforms.XB, [Platforms.PC, Platforms.PS]),
    (Platforms.PC, [Platforms.XB, Platforms.PS]),
    (Platforms.PS, [Platforms.PC, Platforms.XB])
])
async def test_find_rat_incorrect_platform(rat_cache_fx, actual, invalids):
    """
    Verifies that `Rat.get_rat_by_name` called with a specific platform that does not match
        the stored platform returns None
    """
    Rat(name="UNIT_TEST", uuid=None, platform=actual)
    for platform in invalids:
        found_rat = await rat_cache_fx.get_rat_by_name(name="UNIT_TEST", platform=platform)

        assert found_rat is None


async def test_find_rat_by_name_not_existing(rat_cache_fx):
    """
    Verifies a cache miss on ratname returns None
    """
    found = await rat_cache_fx.get_rat_by_name(name="uhhh")
    assert found is None

    found = await rat_cache_fx.get_rat_by_name(name="chapstix", platform=Platforms.XB)
    assert found is None


async def test_by_uuid_setter_valid(rat_cache_fx: RatCache, rat_good_fx: Rat):
    fdict = {rat_good_fx.uuid: rat_good_fx}
    rat_cache_fx.by_uuid = fdict
    assert fdict == rat_cache_fx.by_uuid


@pytest.mark.parametrize("garbage", [None, -1, 2.42, "pink salad", []])
async def test_by_uuid_setter_invalid(garbage, rat_cache_fx):
    with pytest.raises(TypeError):
        rat_cache_fx.by_uuid = garbage


async def test_by_name_setter_valid(rat_cache_fx, rat_good_fx: Rat):
    fdict = {rat_good_fx.name: rat_good_fx}

    rat_cache_fx.by_name = fdict
    assert fdict == rat_cache_fx.by_name


@pytest.mark.parametrize("garbage", [None, -1, 2.42, "pink salad", []])
async def test_by_name_setter_garbage(rat_cache_fx: RatCache, garbage):
    with pytest.raises(TypeError):
        rat_cache_fx.by_name = garbage


async def test_flush(rat_cache_fx: RatCache):
    rat_cache_fx.by_name = {"s": 12}
    rat_cache_fx.by_uuid = {uuid4(): 12}

    rat_cache_fx.flush()
    assert {} == rat_cache_fx.by_uuid
    assert {} == rat_cache_fx.by_name


@pytest.mark.usefixtures('reset_rat_cache_fx')
async def test_singleton():
    """Verifies rat_cache acts as a singleton"""
    alpha = RatCache()
    beta = RatCache()
    assert alpha is beta
