"""
test_rescue.py - tests for Rescue and RescueBoard objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock

from Modules.rat_rescue import Rescue


class TestRescue(TestCase):
    """
    Tests for `Modules.Rescue.Rescue`
    """

    def setUp(self):
        self.time = datetime(2017, 12, 24, 23, 59, 49)
        self.system = "firestone"
        self.case_id = "some_id"
        self.rescue = Rescue(self.case_id, "stranded_commander", system=self.system, created_at=self.time)

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
        Verifies the default settings for `Rescue.quotes` property are set correctly
        And confirms the property is readable.\n
        :return:
        :rtype:
        """
        self.assertEqual([], self.rescue.quotes)

    def test_write_quotes_correctly(self):
        """
        Verifies the `Rescue.quotes` property can be written to when given a list
        :return:
        :rtype:
        """
        self.rescue.quotes = ["foo"]
        self.assertEqual(["foo"], self.rescue.quotes)

    def test_write_quotes_incorrectly(self):
        """
        Verifies `Rescue.quotes` cannot be set to wierd things that are not lists
        :return:
        :rtype:
        """
        names = [False, True, "string", {}, 12]
        for name in names:
            with self.assertRaises(ValueError):
                self.rescue.quotes = name

    def test_add_quote(self):
        # verify the list was empty
        self.assertEqual(self.rescue.quotes, [])
        # add ourselves a quote
        self.rescue.add_quote(message="foo", author='unit_test[BOT]')
        # verify something got written to the rescue property
        self.assertEqual(1, len(self.rescue.quotes))
        # now verify that something is what we wanted to write
        self.assertEqual("foo", self.rescue.quotes[0].message)
        self.assertEqual("unit_test[BOT]", self.rescue.quotes[0].author)

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
        verifies attempts to set `Rescue.board_index` to things other than ints, or below zero,
        Fail with the correct errors.
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
