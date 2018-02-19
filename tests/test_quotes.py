"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import datetime
from unittest import TestCase, expectedFailure

from Modules.rat_rescue import Quotes


class TestQuotes(TestCase):

    def setUp(self):
        pass

    def test_message(self):
        """
        Verifies functionality of the default constructor
        """
        expectedMessage = "some test message"
        quote = Quotes(message=expectedMessage)
        self.assertEqual(expectedMessage, quote.message)
        self.assertEqual("Mecha", quote.author)

    def test_message_setter(self):
        """
        Verifies Quote.message property is writable.
        :return:
        :rtype:
        """
        expected_message = "my glorious message"
        quote = Quotes(message="foo")
        quote.message = expected_message
        self.assertEqual(expected_message, quote.message)

    def test_author(self):
        """
        Verifies `Quotes.author` gets set correctly during creation
        :return:
        :rtype:
        """
        expected_author = "unit_test[BOT]"
        quote = Quotes(message="foo", author=expected_author)
        self.assertEqual(expected_author, quote.author)

    def test_author_is_readonly(self):
        """
        verifies `Quotes.author` is a readonly property.
        :return:
        :rtype:
        """
        quote = Quotes("foo")
        with self.assertRaises(AttributeError):
            quote.author = "unit_test[BOT]"

    def test_created_at(self):
        expected_time = datetime.datetime.utcnow()
        quote = Quotes(message="foo", created_at=expected_time)
        self.assertEqual(quote.created_at, expected_time)

    def test_updated_at_setter_valid(self):
        """
        Verifies `Quotes.updated_at` is writable given correct parameters
        :return:
        :rtype:
        """
        expected_time = datetime.datetime.utcnow()
        quote = Quotes(message="foo", updated_at=expected_time)

        self.assertEqual(expected_time, quote.updated_at)

        quote.updated_at = expected_time = datetime.datetime.utcnow()
        self.assertEqual(expected_time, quote.updated_at)

    def test_updated_at_invalid(self):
        """
        Verifies writing garbage to `Quotes.updated_at` raises expected Error.
        :return:
        :rtype:
        """
        quote = Quotes("foobar")
        bad_values = [12, False, ["foo"], "bar", None]
        for value in bad_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    quote.updated_at = value

    def test_last_author_setter_invalid(self):
        """
        Verifies `Quotes.last_author` can be written to
        :return:
        :rtype:
        """
        quote = Quotes("foobar")
        bad_values = [12, False, ["foo"], None]
        for value in bad_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    quote.last_author = value

    @expectedFailure
    def test_modify(self):
        self.fail()

    @expectedFailure
    def test_new(self):
        self.fail()
