from unittest import TestCase
from uuid import UUID

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

    def test_find_rat_by_name_existing(self):
        """
        Verifies that cached rats can be found by name
        """
        found_rat = Rats.get_rat(name="UNIT_TEST")
        self.assertEqual(found_rat, self.my_rat)

    def test_find_rat_incorrect_platform(self):
        """
        Verifies that `Rats.get_rat` called with a specific platform that does not match
            the stored platform returns None
        """
        found_rat = Rats.get_rat(name="UNIT_TEST", platform=Platforms.XB)
        self.assertIsNone(found_rat)

    def test_find_rat_bad_type(self):
        """
        Verifies that attempting to throw garbage at Rats.search() raises the proper exception
        """
        garbage = ['foo', -42, 42, 0, False, True]
        for piece in garbage:
            # self.fail("Not implemented yet, as the functionality doesn't exist!")
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    Rats.get_rat(name=piece)
                    Rats.get_rat(name="foo", platform=piece)

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
