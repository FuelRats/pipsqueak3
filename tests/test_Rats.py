from unittest import TestCase
from uuid import UUID, uuid4

import pytest

from Modules.rat_rescue import Rescue
from Modules.rats import Rats
from ratlib.names import Platforms


class TestRat(TestCase):
    """
    Test suite for `Rescue.Rats`
    """

    def setUp(self):
        """
        Setup operations to run before every test
        Returns:

        """
        # purge the cache
        Rats.flush()
        # generate a uuid
        self.some_id = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")

        # make a rat
        self.my_rat = Rats(uuid=self.some_id, name="UNIT_TEST", platform=Platforms.PC)

    def test_new_instance(self):
        """
        Verifies creating a new instance of `Rats` functions as expected

        Returns:

        """
        # generate a uuid
        some_id = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")

        # make a rat
        my_rat = self.my_rat
        # verify its properties
        self.assertEqual("UNIT_TEST", my_rat.name)
        self.assertEqual(some_id, my_rat.uuid)

        # verify the caches got touched. (function verified in different test)
        self.assertNotEqual({}, my_rat.cache_by_name)
        self.assertNotEqual({}, my_rat.cache_by_id)

    def test_update_cache_on_new_instance(self):
        """
        Verifies both caches got correctly updated when a new Rat is
         instantiated.
        """

        # verify the keys exist and store the expected data
        self.assertEqual(Rats.cache_by_id[self.some_id], self.my_rat)
        self.assertEqual(Rats.cache_by_name["UNIT_TEST"], self.my_rat)

    def test_first_limpet(self):
        """
        Verifies `Rescue.first_limpet` behaves as expected.
        """
        rescue = Rescue(None, "UNIT_TEST", "FOOBAR", "unit_test")
        with self.subTest(mode="default"):
            # verify default state
            self.assertIsNone(rescue.first_limpet)

        guid = uuid4()

        with self.subTest(mode="uuid", guid=guid):
            rescue.first_limpet = guid
            self.assertEqual(rescue.first_limpet, guid)

        # reset for next subtest
        rescue._firstLimpet = None
        guid_str = str(guid)
        with self.subTest(mode="good string", guid=guid_str):
            rescue.first_limpet = guid_str
            self.assertEqual(rescue.first_limpet, guid)

        rescue._firstLimpet = None
        garbage = [[], {}, "foo", "bar", -2]
        for piece in garbage:
            with self.subTest(mode="garbage", piece=piece):
                with self.assertRaises(TypeError):
                    rescue.first_limpet = piece

    def test_name_good_type(self):
        """
        Verifies `Rats.name` can be set when given good data
        """
        good_names = ["foo", "bar22", "potato"]
        for name in good_names:
            with self.subTest(name=name):
                self.my_rat.name = name
                self.assertEqual(self.my_rat.name, name)

    def test_name_bad_type(self):
        """
        Verifies `Rats.name` raises a type error when someone throws garbage
         at it.
        """
        bad_names = [42, -0.02, None, [], {}, self.some_id]
        for name in bad_names:
            with self.subTest(name=name):
                with self.assertRaises(TypeError):
                    self.my_rat.name = bad_names

    def test_uuid_good_type(self):
        """
        Verifies `Rats.uuid` can me set when given good data.
        """
        good_id = [UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                   "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"]
        for val in good_id:
            with self.subTest(val=val):
                self.my_rat.uuid = val
                try:
                    self.assertEqual(val, self.my_rat.uuid)
                except AssertionError:
                    self.assertEqual(UUID(val), self.my_rat.uuid)

    def test_uuid_bad_types(self):
        """
        Verifies `Rats.uuid` raises a TypeError when someone throws garbage
        at it.
        """
        bad_types = [42, -0.02, None, [], {}]
        for name in bad_types:
            with self.subTest(name=name):
                with self.assertRaises(TypeError):
                    self.my_rat.uuid = bad_types


class TestRatsPyTest(object):
    @pytest.mark.parametrize("platform", [
        Platforms.XB,
        Platforms.PC,
        Platforms.PS,
        Platforms.DEFAULT
    ])
    def test_rat_platforms(self, platform: Platforms):
        my_rat = Rats(uuid=uuid4(), name="foo", platform=platform)
        assert platform == my_rat.platform

    @pytest.mark.parametrize("garbage", [
        None,
        (None,),
        [],
        {}
    ])
    def test_platform_garbage(self, garbage):
        """
        Verifies a TypeError is raised when attempting to set Rats.platform to garbage

        Args:
            garbage ():
        """
        my_rat = Rats(None, "potato", Platforms.PC)
        with pytest.raises(TypeError):
            my_rat.platform = garbage

    @pytest.mark.asyncio
    @pytest.mark.parametrize("garbage", [22.1, -42, 42, 0, False, True])
    async def test_find_rat_by_name_bad_type(self, garbage):
        """
        Verifies that attempting to throw garbage at Rats.search() raises the proper exception
        """
        with pytest.raises(TypeError):
            await Rats.get_rat_by_name(name=garbage)

        with pytest.raises(TypeError):
            await Rats.get_rat_by_name(name="foo", platform=garbage)

    @pytest.mark.asyncio
    async def test_find_rat_by_name_not_in_cache_and_no_API(self):
        """
        Verifies the functionality of Rats.get_rat_by_nickname when the rat is not in the cache
        """
        result = await Rats.get_rat_by_name(name="somenamethatdoesnotexist")
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("garbage", [22.1, -42, 42, 0, False, True])
    async def test_get_rat_by_uuid_garbage(self, garbage):
        with pytest.raises(TypeError):
            await Rats.get_rat_by_uuid(uuid=garbage)

    @pytest.mark.asyncio
    async def test_get_rat_by_uuid_cache_miss(self):
        """Verifies Rats.get_rat_by_uuid returns None upon cache miss and no API connection"""
        uuid = uuid4()
        assert await Rats.get_rat_by_uuid(uuid) is None

    @pytest.mark.asyncio
    async def test_get_rat_by_uuid_cache_hit(self, RatGood_fx: Rats):
        """Verifies Rats.get_rat_by_uuid returns the correct rat on cache hit"""
        mine = RatGood_fx
        found = await Rats.get_rat_by_uuid(mine.uuid)
        assert found is not None
        assert found == mine

    def test_rat_eq_true(self, RatGood_fx: Rats):
        """Verifies Rats.__eq__ functions correctly against equal objects"""
        assert RatGood_fx == RatGood_fx

    def test_rat_eq_None(self, RatGood_fx: Rats):
        """Verifies Rats.__eq__ functions correctly against None"""
        # because object is nullable, therefore must be able to handle None.
        assert RatGood_fx != None

    @pytest.mark.asyncio
    async def test_find_rat_by_name_existing(self, RatGood_fx: Rats):
        """
        Verifies that cached rats can be found by name
        """
        found_rat = await Rats.get_rat_by_name(name=RatGood_fx.name)
        assert RatGood_fx == found_rat

    @pytest.mark.asyncio
    async def test_find_rat_incorrect_platform(self):
        """
        Verifies that `Rats.get_rat_by_name` called with a specific platform that does not match
            the stored platform returns None
        """
        Rats(name="UNIT_TEST", uuid=None, platform=Platforms.PC)

        found_rat = await Rats.get_rat_by_name(name="UNIT_TEST", platform=Platforms.XB)

        assert found_rat is None
        # pytest.fail("not awaited!")
