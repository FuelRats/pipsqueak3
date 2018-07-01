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


@pytest.fixture(scope="session")
@pytest.mark.useFixture("dbm_fx")
@pytest.mark.asyncio
async def prepare_facts(dbm_fx: database_manager.DatabaseManager):
    pass


@pytest.mark.database
@pytest.mark.asyncio
class TestFacts(object):

    @pytest.mark.asyncio
    @classmethod
    async def setup_class(cls):
        dbm_fx = database_manager.DatabaseManager()
        await dbm_fx.create_table("testfacts",
                                  {"name": "VARCHAR", "lang": "VARCHAR", "message": "VARCHAR", "author": "VARCHAR"})
        await dbm_fx.insert_row("testfacts", ("test1", "en", "THIS IS TEST No. 1", "TestRat"))
        await dbm_fx.insert_row("testfacts", ("test1", "de", "Icke bin Test #1", "TestRat"))

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

        await facts_fx.set_fact("test2", "I want my cake!", "RatFest", "en")
        value = await facts_fx.get_fact("test2", "en")
        assert value == "I want my cake!"

    async def test_delete_fact(self, facts_fx: rat_facts.FactsManager):
        value = await facts_fx.is_fact("test1", "de")
        assert value

        await facts_fx.delete_fact("test1", "de")

        value = await facts_fx.is_fact("test1", "de")
        assert not value