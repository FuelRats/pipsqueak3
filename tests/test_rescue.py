"""
test_rescue.py - tests for Rescue and RescueBoard objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
from datetime import datetime
from unittest import TestCase, expectedFailure
from unittest.mock import patch, MagicMock
from uuid import UUID, uuid4

from Modules.rat_rescue import Rescue, Rats


class TestRescue(TestCase):
    """
    Tests for `Modules.Rescue.Rescue`
    """

    def setUp(self):
        self.time = datetime(2017, 12, 24, 23, 59, 49)
        self.updated_at = datetime(2017, 12, 24, 23, 59, 52)
        self.system = "firestone"
        self.case_id = "some_id"
        self.rescue = Rescue(self.case_id, "stranded_commander",
                             system=self.system, created_at=self.time,
                             updated_at=self.updated_at,
                             irc_nickname="stranded_commander")

    def test_client_property_exists(self):
        """
        Verifies the `Rescue.client` property exists\n
        :return:
        :rtype:
        """
        self.assertTrue(hasattr(self.rescue, "client"))
        self.assertEqual(self.rescue.client, "stranded_commander")

    def test_client_writeable(self):
        """
        Verifies the `Rescue.client` property can be written to correctly\n
        :return:
        :rtype:
        """
        expected = "some other commander"
        self.rescue.client = expected
        self.assertEqual(self.rescue.client, expected)

    def test_created_at_made_correctly(self):
        """
        Verifies the `Rescue.created_at` property was correctly created\n
        :return:
        :rtype:
        """
        self.assertEqual(self.time, self.rescue.created_at)

    def test_created_at_not_writable(self):
        """
        Verifies the `Rescue.created_at` property cannot be written to\n
        :return:
        :rtype:
        """
        with self.assertRaises(AttributeError):
            self.rescue.created_at = datetime.utcnow()

    def test_updated_at_initial(self):
        """
        Verify `Rescue.updated_at` was initialized correctly.

        Returns:

        """
        self.assertEqual(self.updated_at, self.rescue.updated_at)

    def test_updated_at_settable_correctly(self):
        """
        Verifies `Rescue.updated_at` can be set properly

        Returns:

        """
        my_time = datetime.now()
        self.rescue.updated_at = my_time
        self.assertEqual(my_time, self.rescue.updated_at)

    def test_updated_at_value_error(self):
        """
        Verifies `Rescue.updated_at` returns a `ValueError` if a bad date is
         given.

        Returns:

        """
        with self.assertRaises(ValueError):
            self.rescue.updated_at = datetime(2012, 1, 1, 1, 1, 1)

    def test_updated_at_type_error(self):
        """
        Verifies `Rescue.updated_at` raises a `TypeError` when someone throws
        garbage at it

        Returns:

        """
        garbage = [12, "foo", [], {}, False, None]
        for value in garbage:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    self.rescue.updated_at = value

    def test_system_initial_set(self):
        """
        Verifies the `Rescue.system` property was correctly set during init\n
        :return:
        :rtype:
        """
        self.assertEqual(self.system.upper(), self.rescue.system)

    def test_system_writable(self):
        self.rescue.system = "sol"
        self.assertEqual(self.rescue.system, "SOL")

    def test_case_id(self):
        self.assertEqual(self.case_id, self.rescue.case_id)

    def test_get_active(self):
        """
        Verifies `Rescue.active` is readable and set correctly by default
        :return:
        :rtype:
        """
        self.assertTrue(self.rescue.active)

    def test_set_active_correctly(self):
        """
        Tests the `Rescue.active` property for expected function
        :return:
        :rtype:
        """
        states = [True, False]
        for state in states:
            with self.subTest(state=state):
                self.rescue.active = state

    def test_set_active_set_incorrectly(self):
        """
        Tests the `Rescue.active` property for the correct usage errors
        :return:
        :rtype:
        """
        with self.assertRaises(ValueError):
            self.rescue.active = "something totally not right"

    def test_get_quotes(self):
        """
        Verifies the default settings for `Rescue.quotes` property are set
        correctly And confirms the property is readable.\n
        :return:
        :rtype:
        """
        self.assertEqual([], self.rescue.quotes)

    def test_write_quotes_correctly(self):
        """
        Verifies the `Rescue.quotes` property can be written to when given a
        list

        :return:
        :rtype:
        """
        self.rescue.quotes = ["foo"]
        self.assertEqual(["foo"], self.rescue.quotes)

    def test_write_quotes_incorrectly(self):
        """
        Verifies `Rescue.quotes` cannot be set to wierd things that are not
         lists

        :return:
        :rtype:
        """
        names = [False, True, "string", {}, 12]
        for name in names:
            with self.assertRaises(ValueError):
                self.rescue.quotes = name

    def test_add_quote_with_name(self):
        # verify the list was empty
        self.assertEqual(self.rescue.quotes, [])
        # add ourselves a quote
        self.rescue.add_quote(message="foo", author='unit_test[BOT]')
        # verify something got written to the rescue property
        self.assertEqual(1, len(self.rescue.quotes))
        # now verify that something is what we wanted to write
        self.assertEqual("foo", self.rescue.quotes[0].message)
        self.assertEqual("unit_test[BOT]", self.rescue.quotes[0].author)

    def test_add_quote_mecha(self):
        # verify the list was empty
        self.assertEqual(self.rescue.quotes, [])
        # add ourselves a quote
        self.rescue.add_quote(message="foo")
        # verify something got written to the rescue property
        self.assertEqual(1, len(self.rescue.quotes))
        # now verify that something is what we wanted to write
        self.assertEqual("foo", self.rescue.quotes[0].message)
        self.assertEqual("Mecha", self.rescue.quotes[0].author)

    @patch('tests.test_rescue.Rescue.updated_at')
    def test_change_context_manager(self, mock_updated_at: MagicMock):
        """
        Verifies the `Rescue.change` context manager functions as expected.
        Currently that is simply to update the `Rescue.updated_at` is updated.
        Returns:

        """
        origin = self.rescue.updated_at
        with self.rescue.change():
            pass
        self.assertNotEqual(origin, self.rescue.updated_at)

    def test_set_board_index_correctly(self):
        """
        Verifies `Rescue.board_index` is settable

        Returns:
        """
        self.rescue.board_index = 24
        self.assertEqual(24, self.rescue.board_index)

    def test_set_board_index_incorrectly(self):
        """
        verifies attempts to set `Rescue.board_index` to things other than
        ints, or below zero, Fail with the correct errors.
        Returns:

        """
        bad_values_type = ["foo", [], {}]
        bad_values_ints = [-42, -2]
        for value in bad_values_ints:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.rescue.board_index = value

        for value in bad_values_type:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    self.rescue.board_index = value

    def test_unidentified_rats_properly(self):
        """
        Verifies `Rescue.unidentified_rats` can be written to with good data

        Returns:

        """
        # verify it was empty to begin with (default)
        self.assertEqual(self.rescue.unidentified_rats, [])
        # lets make some names
        names = ["UNIT_TEST[BOT]", "flying_potato", "random_person"]
        # set the property
        self.rescue.unidentified_rats = names
        # verify the property.
        self.assertEqual(self.rescue.unidentified_rats, names)

    def test_unidentified_rats_bad_types(self):
        """
        Verifies the correct exception is raised when someone throws garbage
        at `Rescue.unidentified_rats`

        Returns:

        """
        garbage = [None, "foo", {}, 12, 22.3]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.unidentified_rats = piece

    def test_is_open_properly(self):
        """
        Verifies `Rescue.is_open` is readable and settable when thrown good
        parameters

        Returns:

        """
        # check default state
        self.assertTrue(self.rescue.is_open)

        data = [True, False]
        for value in data:
            with self.subTest(value=value):
                self.rescue.is_open = value
                self.assertEqual(self.rescue.is_open, value)

    def test_is_open_bad_types(self):
        """
        Verifies `Rescue.is_open` raises correct exceptions when its given
        garbage

        Returns:

        """
        garbage = [None, "foo", {}, 12, 22.3]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.is_open = piece

    def test_epic_readable(self):
        """
        Verifies  `Rescue.epic` is readable.

        Returns:

        """
        # check default state
        self.assertFalse(self.rescue.epic)

    def test_code_red_properly(self):
        """
        Verifies `Rescue.code_red` is readable and settable when thrown good
        parameters

        Returns:

        """
        # check default state
        self.assertFalse(self.rescue.code_red)

        data = [True, False]
        for value in data:
            with self.subTest(value=value):
                self.rescue.code_red = value
                self.assertEqual(self.rescue.code_red, value)

    def test_code_red_bad_types(self):
        """
        Verifies `Rescue.code_red` raises correct exceptions when its given
         garbage

        Returns:

        """
        garbage = [None, "foo", {}, 12, 22.3]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.code_red = piece

    def test_successful_correctly(self):
        """
        Verifies `Rescue.successful` is readable and settable when thrown good
         parameters

        Returns:

        """
        # check default state
        self.assertFalse(self.rescue.successful)

        data = [True, False]
        for value in data:
            with self.subTest(value=value):
                self.rescue.successful = value
                self.assertEqual(self.rescue.successful, value)

    def test_successful_bad_types(self):
        """
        Verifies `Rescue.successful` raises correct exceptions when its given
        garbage

        Returns:

        """
        garbage = [None, "foo", {}, 12, 22.3]
        for piece in garbage:
            with self.subTest(piece=piece):
                with self.assertRaises(TypeError):
                    self.rescue.successful = piece


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
        self.my_rat = Rats(uuid=self.some_id, name="UNIT_TEST")

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

    def test_find_rat_by_uuid_existing(self):
        """
        Verify that cached rats can be found by uuid
        """
        found_rat = Rats.get_rat(uuid=self.some_id)
        self.assertEqual(self.my_rat, found_rat)

    def test_find_rat_by_uuid_and_name_existing(self):
        """
        Verify that cached rats can be found exactly by uuid and name
        """
        my_uuid = uuid4()
        my_rat = Rats(my_uuid, "foo")
        found = Rats.get_rat(name="foo", uuid=my_uuid)
        self.assertEqual(my_rat, found)

    @expectedFailure
    def test_find_rat_bad_type(self):
        """
        Verifies that attempting to throw garbage at Rats.search() raises the proper exception
        """
        garbage = ['foo', -42, 42, 0, False, True]
        for piece in garbage:
            self.fail("Not implemented yet, as the functionality doesn't exist!")
            with self.subTest(piece=piece):
                pass

    def test_find_rat_defaults(self):
        """
        Verifies a ValueError is raised when someone calls `Rats.get_rat` with default params
        """
        with self.assertRaises(ValueError):
            Rats.get_rat()

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
