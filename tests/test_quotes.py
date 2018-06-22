"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import datetime

import pytest

from Modules.rat_quotation import Quotation


class TestQuotes(object):

    def test_message(self):
        """
        Verifies functionality of the default constructor
        """
        expectedMessage = "some test message"
        quote = Quotation(message=expectedMessage)
        assert expectedMessage == quote.message
        assert "Mecha" == quote.author

    def test_message_setter(self):
        """
        Verifies Quote.message property is writable.
        :return:
        :rtype:
        """
        expected_message = "my glorious message"
        quote = Quotation(message="foo")
        quote.message = expected_message
        assert expected_message == quote.message

    def test_author(self):
        """
        Verifies `Quotation.author` gets set correctly during creation
        :return:
        :rtype:
        """
        expected_author = "unit_test[BOT]"
        quote = Quotation(message="foo", author=expected_author)
        assert expected_author == quote.author

    def test_author_is_readonly(self):
        """
        verifies `Quotation.author` is a readonly property.
        :return:
        :rtype:
        """
        quote = Quotation("foo")
        with pytest.raises(AttributeError):
            quote.author = "unit_test[BOT]"

    def test_created_at(self):
        expected_time = datetime.datetime.utcnow()
        quote = Quotation(message="foo", created_at=expected_time)
        assert quote.created_at == expected_time

    def test_updated_at_setter_valid(self):
        """
        Verifies `Quotation.updated_at` is writable given correct parameters
        :return:
        :rtype:
        """
        expected_time = datetime.datetime.utcnow()
        quote = Quotation(message="foo", updated_at=expected_time)

        assert expected_time == quote.updated_at

        quote.updated_at = expected_time = datetime.datetime.utcnow()
        assert expected_time == quote.updated_at

    @pytest.mark.parametrize("garbage", [12, False, ["foo"], "bar", None])
    def test_updated_at_invalid(self, garbage):
        """
        Verifies writing garbage to `Quotation.updated_at` raises expected
        Error when garbage is thrown at it

        """
        quote = Quotation("foobar")
        with pytest.raises(ValueError):
            quote.updated_at = garbage

    @pytest.mark.parametrize("garbage", [12, False, ["foo"], None])
    def test_last_author_setter_invalid(self, garbage):
        """
        Verifies `Quotation.last_author` can be written to
        :return:
        :rtype:
        """
        quote = Quotation("foobar")

        with pytest.raises(ValueError):
            quote.last_author = garbage

    def test_modify(self, context_fx):
        """
        Verifies a quote can be changed correctly, that the correct fields are
         set
        """

        quote = Quotation("foo")
        quote.modify(context_fx, message="bar")
        assert "bar" == quote.message
        assert quote.created_at != quote.updated_at
        assert quote.author != quote.last_author
