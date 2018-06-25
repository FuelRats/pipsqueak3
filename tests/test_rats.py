from uuid import uuid4

import pytest

from Modules.rat import Rat
from utils.ratlib import Platforms


@pytest.mark.rat
class TestRatsPyTest(object):
    @pytest.mark.parametrize("platform", [
        Platforms.XB,
        Platforms.PC,
        Platforms.PS,
        Platforms.DEFAULT
    ])
    def test_rat_platforms(self, platform: Platforms):
        my_rat = Rat(uuid=uuid4(), name="foo", platform=platform)
        assert platform == my_rat.platform

    @pytest.mark.parametrize("garbage", [
        None,
        (None,),
        [],
        {}
    ])
    def test_platform_garbage(self, garbage):
        """
        Verifies a TypeError is raised when attempting to set Rat.platform to garbage

        Args:
            garbage ():
        """
        my_rat = Rat(None, "potato", Platforms.PC)
        with pytest.raises(TypeError):
            my_rat.platform = garbage

    @pytest.mark.asyncio
    @pytest.mark.parametrize("garbage", [22.1, -42, 42, 0, False, True])
    async def test_find_rat_by_name_bad_type(self, garbage, rat_cache_fx):
        """
        Verifies that attempting to throw garbage at Rat.search() raises the proper exception
        """
        with pytest.raises(TypeError):
            await rat_cache_fx.get_rat_by_name(name=garbage)

        with pytest.raises(TypeError):
            await rat_cache_fx.get_rat_by_name(name="foo", platform=garbage)

    @pytest.mark.asyncio
    async def test_find_rat_by_name_not_in_cache_and_no_API(self, rat_cache_fx):
        """
        Verifies the functionality of Rat.get_rat_by_nickname when the rat is not in the cache
        """
        result = await rat_cache_fx.get_rat_by_name(name="somenamethatdoesnotexist")
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("garbage", [22.1, -42, 42, 0, False, True])
    async def test_get_rat_by_uuid_garbage(self, garbage, rat_cache_fx):
        with pytest.raises(TypeError):
            await rat_cache_fx.get_rat_by_uuid(uuid=garbage)

    @pytest.mark.asyncio
    async def test_get_rat_by_uuid_cache_miss(self, rat_cache_fx):
        """Verifies Rat.get_rat_by_uuid returns None upon cache miss and no API connection"""
        uuid = uuid4()
        assert await rat_cache_fx.get_rat_by_uuid(uuid) is None

    @pytest.mark.asyncio
    async def test_get_rat_by_uuid_cache_hit(self, rat_good_fx: Rat, rat_cache_fx):
        """Verifies Rat.get_rat_by_uuid returns the correct rat on cache hit"""
        mine = rat_good_fx
        found = await rat_cache_fx.get_rat_by_uuid(mine.uuid)
        assert found is not None
        assert found == mine

    def test_rat_eq_true(self, rat_good_fx: Rat):
        """Verifies Rat.__eq__ functions correctly against equal objects"""
        assert rat_good_fx == rat_good_fx

    def test_rat_eq_None(self, rat_good_fx: Rat):
        """Verifies Rat.__eq__ functions correctly against None"""
        # because object is nullable, therefore must be able to handle None.
        assert rat_good_fx != None

    @pytest.mark.asyncio
    async def test_find_rat_by_name_existing(self, rat_good_fx: Rat, rat_cache_fx):
        """
        Verifies that cached rats can be found by name
        """
        found_rat = await rat_cache_fx.get_rat_by_name(name=rat_good_fx.name)
        assert rat_good_fx == found_rat

    @pytest.mark.asyncio
    async def test_find_rat_incorrect_platform(self, rat_cache_fx):
        """
        Verifies that `Rat.get_rat_by_name` called with a specific platform that does not match
            the stored platform returns None
        """
        Rat(name="UNIT_TEST", uuid=None, platform=Platforms.PC)

        found_rat = await rat_cache_fx.get_rat_by_name(name="UNIT_TEST", platform=Platforms.XB)

        assert found_rat is None
        # pytest.fail("not awaited!")
