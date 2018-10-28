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
from Modules.rat_facts import Fact
import datetime


@pytest.fixture
@pytest.mark.asyncio
async def prepare_facts(dbm_fx: database_manager.DatabaseManager):
    if not dbm_fx.marker:
        dbm_fx.marker_facts = True
        await dbm_fx.insert_row("fact",
                                {"name": "test1", "lang": "en", "message": "THIS IS TEST No. 1",
                                 "author": "TestRat"},
                                ("name", "lang"))
        await dbm_fx.insert_row("fact",
                                {"name": "test1", "lang": "de", "message": "Icke bin Test #1",
                                 "author": "TestRat"},
                                ("name", "lang"))
        yield
        await dbm_fx.insert_row("fact",
                                {"name": "test1", "lang": "de", "message": "Icke bin Test #1",
                                 "author": "TestRat"},
                                ("name", "lang"))
        await dbm_fx.delete_row("fact", "AND", {"name": "test2", "lang": "en"})


@pytest.mark.database
@pytest.mark.asyncio
@pytest.mark.usefixtures("prepare_facts")
class TestFacts(object):

    async def test_get_fact(self, facts_fx: rat_facts.FactsManager):
        # getting a fact and verifying it is the right language
        value = (await facts_fx.get_fact("test1", "en")).message
        assert value == "THIS IS TEST No. 1"

        # same with the next language
        value = (await facts_fx.get_fact("test1", "de")).message
        assert value == "Icke bin Test #1"

        # this one does not exist (yet), so it returns None
        value = await facts_fx.get_fact("test1", "es")
        assert value is None

    async def test_is_fact(self, facts_fx: rat_facts.FactsManager):
        # this should be a fact, we "created" it during setUp
        value = await facts_fx.is_fact("test1", "de")
        assert value

        # this one we didn't, so it shouldn't be one at all
        value = await facts_fx.is_fact("test1", "tr")
        assert not value

    async def test_set_fact(self, facts_fx: rat_facts.FactsManager):
        # the fact shouldn't exist in the first place
        value = await facts_fx.is_fact("test2", "en")
        assert not value

        # we set the fact and make sure it's there
        await facts_fx.set_fact(Fact("test2", "en", "I want my cake!", "FatRat",
                                     datetime.datetime.now(tz=datetime.timezone.utc)))
        value = (await facts_fx.get_fact("test2", "en"))
        assert value.message == "I want my cake!"
        first_ts = datetime.datetime.utcnow()
        assert value.timestamp < first_ts

        # and now we re-set it, effectively updating it.
        await facts_fx.set_fact(Fact("test2", "en", "You promised me some Cake!", "AngryFatRat",
                                     datetime.datetime.now(tz=datetime.timezone.utc)))

        # as well as making sure it did what we asked for
        value = (await facts_fx.get_fact("test2", "en"))
        assert value.message == "You promised me some Cake!"
        assert first_ts < value.timestamp

        # and no, you ain't getting your cake!

    async def test_delete_fact(self, facts_fx: rat_facts.FactsManager):
        # make sure we actually have that fact stored
        value = await facts_fx.is_fact("test1", "de")
        assert value

        # kick the fact out of the DB
        await facts_fx.delete_fact("test1", "de")

        # and now the fact should be gone
        value = await facts_fx.is_fact("test1", "de")
        assert not value

    async def test_rule(self, facts_fx, bot_fx):

        # field to store the reply in
        bot_fx.rat_facts_reply = ""

        # mocking the Context class to better control what happens
        class MockContext:
            words = ("!go",)

            # noinspection PyMethodParameters
            def reply(msg: str):  # Note: no self here, works without
                bot_fx.rat_facts_reply = msg
        context = await Context.from_message(bot_fx, "#unit_test", "some_recruit", "!go")
        monkeypatch.setattr(context, "reply", async_callable_fx)  # patch the reply function
        # noinspection PyTypeChecker
        # shouldn't reply, as this is an "internal" fact
        await facts_fx.handle_fact(MockContext)

        # checking it did not reply, or replied with an empty string
        assert not async_callable_fx.was_called

        MockContext.words = ("!test1-en",)
        # noinspection PyTypeChecker
        await facts_fx.handle_fact(MockContext)

        # make sure it pulled the right message
        message = bot_fx.rat_facts_reply
        assert message == "THIS IS TEST No. 1"

    async def test_enabled_property(self, dbm_fx, facts_fx):
        assert dbm_fx.enabled == facts_fx.enabled
        with pytest.raises(AttributeError):
            facts_fx.enabled = False

    @pytest.mark.xfail(reason="Broken in CI")
    async def test_emoji_insert(self, facts_fx: rat_facts.FactsManager):
        await facts_fx.set_fact(Fact("cake", "en", "🥧", "TestUser",
                                     datetime.datetime.now(tz=datetime.timezone.utc)))

        await facts_fx.set_fact(Fact("🥔", "en", "potato", "TestUser",
                                     datetime.datetime.now(tz=datetime.timezone.utc)))

        assert (await facts_fx.get_fact("cake", "en")).message == "🥧"
        assert (await facts_fx.get_fact("🥔", "en")).message == "potato"
