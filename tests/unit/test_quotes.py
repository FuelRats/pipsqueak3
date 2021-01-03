"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
import asyncio
import pendulum
import pytest

from src.packages.quotation.rat_quotation import Quotation


@pytest.mark.unit
@pytest.mark.quotation
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

    def test_created_at(self):
        expected_time = pendulum.now()
        quote = Quotation(message="foo", created_at=expected_time)
        assert quote.created_at == expected_time

    @pytest.mark.asyncio
    async def test_modify(self, context_fx):
        """
        Verifies a quote can be changed correctly, that the correct fields are
         set
        """

        quote = Quotation("foo")
        with quote.modify(context_fx) as some_quote:
            await asyncio.sleep(0.125)
            some_quote.message = "bar"
        assert "bar" == quote.message
        assert quote.created_at != quote.updated_at
        assert quote.author != quote.last_author
