from uuid import uuid4, UUID

import pytest

from Modules.rat import Rat
from utils.ratlib import Platforms


@pytest.mark.rat
class TestRatsPyTest(object):
    @pytest.mark.parametrize("platform", [
        Platforms.XB,
        Platforms.PC,
        Platforms.PS,
        None
    ])
    def test_rat_platforms(self, platform: Platforms, rat_good_fx):
        rat_good_fx.platform = platform
        assert rat_good_fx.platform == platform

    @pytest.mark.parametrize("garbage", [
        -12,
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

    def test_rat_eq_none(self, rat_good_fx: Rat):
        """Verifies Rat.__eq__ functions correctly against None"""
        # because object is nullable, therefore must be able to handle None.
        # noinspection PyComparisonWithNone
        assert rat_good_fx != None

    def test_constructor_cache(self, rat_cache_fx):
        """Verifies constructor behavior with a cache present"""
        uuid = uuid4()
        rat = Rat(uuid, "unit_test[BOT]", Platforms.PC)

        assert Platforms.PC == rat.platform
        assert uuid == rat.uuid
        assert "unit_test[BOT]" == rat.name

        assert rat.name in rat_cache_fx.by_name

    @pytest.mark.parametrize("name", ["snafu", "h0tSh0t99", "clu3l3ss_3xpl0rer99"])
    def test_name_valid(self, name, rat_good_fx: Rat):
        rat_good_fx.name = name
        assert name == rat_good_fx.name

    @pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
    def test_name_garbage(self, garbage, rat_good_fx):
        with pytest.raises(TypeError):
            rat_good_fx.name = garbage

    def test_uuid_strings_invalid(self, rat_good_fx: Rat, random_string_fx):
        with pytest.raises(ValueError):
            rat_good_fx.uuid = random_string_fx

    @pytest.mark.parametrize("uuid_str", ["beeffeed-feed-bad-beef0-00000000beef",
                                          "faff1222-dead-fee-d4412-111111111111"])
    def test_uuid_strings_valid(self, uuid_str: str, rat_good_fx):
        rat_good_fx.uuid = uuid_str
        assert rat_good_fx.uuid == UUID(uuid_str)

    @pytest.mark.parametrize("uuid", [uuid4(), uuid4(), uuid4()])
    def test_uuid_uuids(self, uuid: UUID, rat_good_fx):
        rat_good_fx.uuid = uuid
        assert uuid == rat_good_fx.uuid

    @pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
    def test_uuid_garbage(self, garbage, rat_good_fx):
        with pytest.raises(TypeError):
            rat_good_fx.uuid = garbage
