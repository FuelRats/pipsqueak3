from uuid import uuid4, UUID

import pytest

from src.packages.rat.rat import Rat
from src.packages.utils import Platforms


@pytest.mark.unit
@pytest.mark.rat
class TestRatsPyTest(object):
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

    def test_rat_eq_none(self, rat_good_fx: Rat):
        """Verifies Rat.__eq__ functions correctly against None"""
        # because object is nullable, therefore must be able to handle None.
        # noinspection PyComparisonWithNone
        assert rat_good_fx != None

    def test_constructor_cache(self, rat_cache_fx):
        """Verifies constructor behavior with a cache present"""
        uuid = uuid4()
        rat = Rat(uuid, "unit_test[bot]", Platforms.PC)
        rat_cache_fx.append(rat)
        assert Platforms.PC == rat.platform
        assert uuid == rat.uuid
        assert "unit_test[bot]" == rat.name

        assert rat.name in rat_cache_fx.by_name
