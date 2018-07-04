"""
test_rat_facts.py

Tests for the rat_facts module

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
import pytest
from Modules import rat_facts, database_manager


@pytest.fixture
@pytest.mark.asyncio
async def prepare_facts(dbm_fx: database_manager.DatabaseManager):
    if not len((await dbm_fx.select_rows("fact", "AND", {"name": "test1", "lang": "en"}))) > 0:
        await dbm_fx.insert_row("fact", ("test1", "en", "THIS IS TEST No. 1", "TestRat"))
        await dbm_fx.insert_row("fact", ("test1", "de", "Icke bin Test #1", "TestRat"))
    yield
    await dbm_fx.insert_row("fact", ("test1", "de", "Icke bin Test #1", "TestRat"))
    await dbm_fx.delete_row("fact", "AND", {"name": "test2", "lang": "en"})


@pytest.mark.database
@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_facts")
class TestFacts(object):

    async def test_get_fact(self, facts_fx: rat_facts.FactsManager):
        value = await facts_fx.get_fact("test1", "en")
        assert value == "THIS IS TEST No. 1"

        value = await facts_fx.get_fact("test1", "de")
        assert value == "Icke bin Test #1"

        value = await facts_fx.get_fact("test1", "es")
        assert value is None

    async def test_is_fact(self, facts_fx: rat_facts.FactsManager):
        value = await facts_fx.is_fact("test1", "de")
        assert value

        value = await facts_fx.is_fact("test1", "tr")
        assert not value

    async def test_set_fact(self, facts_fx: rat_facts.FactsManager):
        value = await facts_fx.is_fact("test2", "en")
        assert not value

        await facts_fx.set_fact("test2", "I want my cake!", "FatRat", "en")
        value = await facts_fx.get_fact("test2", "en")
        assert value == "I want my cake!"

        await facts_fx.set_fact("test2", "You promised me some Cake!", "AngryFatRat", "en")
        value = await facts_fx.get_fact("test2", "en")
        assert value == "You promised me some Cake!"

    async def test_delete_fact(self, facts_fx: rat_facts.FactsManager):
        value = await facts_fx.is_fact("test1", "de")
        assert value

        await facts_fx.delete_fact("test1", "de")

        value = await facts_fx.is_fact("test1", "de")
        assert not value

    async def test_rule(self, facts_fx):
        import tests.mock_bot
        tests.mock_bot.MockBot.rat_facts_reply = ""

        class mock_context:
            words = ("!go",)

            # noinspection PyMethodParameters
            def reply(msg: str): # Note: no self here, works without
                tests.mock_bot.MockBot.rat_facts_reply = msg

        # noinspection PyTypeChecker
        await facts_fx.handle_fact(mock_context)
        assert tests.mock_bot.MockBot.rat_facts_reply == ""

        mock_context.words = ("!test1-en",)
        # noinspection PyTypeChecker
        await facts_fx.handle_fact(mock_context)

        message = tests.mock_bot.MockBot.rat_facts_reply
        assert message == "THIS IS TEST No. 1"
