"""
test_mechaclient.py - tests for src.mechaclient class

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
import pytest

from src.packages.fact_manager import FactManager
from src.packages.board.rat_board import RatBoard
from src.packages.cache.rat_cache import RatCache

from src.packages.commands import command
from src.packages.context.context import Context

pytestmark = pytest.mark.mechaclient


def test_verify_api_handler_private(bot_fx):
    """
    Asserts the private reference for the API handlers is none, after instantiation.
    """
    assert bot_fx._api_handler is None


def test_verify_fact_manager_private(bot_fx):
    """
    Asserts the private reference for the Fact Manager is none, after instantiation.
    """
    assert bot_fx._fact_manager is None


def test_verify_rat_cache_private(bot_fx):
    """
    Asserts the private reference for the Rat Cache is none, after instantiation.
    """
    assert bot_fx._rat_cache is None


def test_verify_rat_board_private(bot_fx):
    """
    Asserts the private reference for the Rat Board is none, after instantiation.
    """
    assert bot_fx._rat_board is None


def test_verify_api_handler(bot_fx):
    """
    Asserts the API handler raises an Attribute error if setting is attempted.
    """
    # Helper Class
    class FakeAPIHandler:
        ...

    assert bot_fx.api_handler is None

    with pytest.raises(AttributeError):
        bot_fx.api_handler = FakeAPIHandler()


@pytest.mark.parametrize("fact_manager_bad_types", ["Something that isn't a Fact Manager",
                                                    (1, 3), RatBoard()])
def test_verify_fact_manager(bot_fx, fact_manager_bad_types):
    """
    Asserts the Fact Manager can be set, requires a FactManager object, and returns properly.
    """
    # Helper Class
    class FakeFactManager(FactManager):
        # Overriding the parent class init to prevent it from creating a DB connection.
        def __init__(self):
            ...

    bot_fx.fact_manager = FakeFactManager()
    assert isinstance(bot_fx._fact_manager, FakeFactManager)
    assert bot_fx.fact_manager is bot_fx._fact_manager

    with pytest.raises(TypeError):
        bot_fx.fact_manager = fact_manager_bad_types


def test_verify_fact_manager_deleter(bot_fx):
    """
    Asserts no error is thrown upon deletion of the fact_manager property.
    """
    # Helper Class
    class FakeFactManager(FactManager):
        # Overriding the parent class init to prevent it from creating a DB connection.
        def __init__(self):
            ...

    bot_fx.fact_manager = FakeFactManager()
    del bot_fx.fact_manager


def test_verify_rat_board_deleter(bot_fx):
    """
    Asserts no error is thrown upon deletion of the rat_board property.
    """
    bot_fx.board = RatBoard()
    del bot_fx.board


@pytest.mark.parametrize("rat_board_bad_types", ["Something that isn't a Rat Board", (1, 3), 3.14])
def test_verify_rat_board(bot_fx, rat_board_bad_types):
    """
    Asserts the Rat Board can be set, requires a Rat Board object, and returns properly.
    """
    bot_fx.board = RatBoard()

    assert isinstance(bot_fx._rat_board, RatBoard)
    assert bot_fx.board is bot_fx._rat_board

    with pytest.raises(TypeError):
        bot_fx.board = rat_board_bad_types


def test_verify_rat_cache(bot_fx, monkeypatch):
    """
    Asserts the Rat Cache can be set, requires a Rat Cache object, and returns properly.
    """
    # Patch this value, as we have no current setter.
    with monkeypatch.context() as monkeypatcher:
        monkeypatcher.setattr(bot_fx, "_rat_cache", RatCache())
        assert bot_fx.rat_cache is bot_fx._rat_cache


@pytest.mark.asyncio
async def test_mechaclient_on_message_anti_loop(bot_fx):
    """
    Asserts IRC lines from the bot itself are properly discarded.
    """
    result = await bot_fx.on_message("#pytesting", "Mechasqueak3-tests[BOT]", "Message")

    assert result is None
    assert not bot_fx.sent_messages


@pytest.mark.parametrize("mechaclient_irc_chatter", ["is this a command?",
                                                     "factadd something horrible",
                                                     "lul, 0mg haxor",
                                                     "wr+ #3",
                                                     "925300 minutes"])
@pytest.mark.parametrize("mechaclient_irc_names", ["rat_2412", "Shaott", "xXxN00BR4TxXx"])
@pytest.mark.asyncio
async def test_mechaclient_on_message_handling(bot_fx, mechaclient_irc_chatter,
                                               mechaclient_irc_names):
    """
    Asserts Incoming IRC chatter (non command) is discarded properly, if not a command.
    """
    result = await bot_fx.on_message("#pytesting", mechaclient_irc_names, mechaclient_irc_chatter)

    assert result is None
    assert not bot_fx.sent_messages


@pytest.mark.asyncio
async def test_mechaclient_on_message_exception(bot_fx):
    """
    Assert an exception is created and output to the user properly, if one occurs.
    """

    # Command Helper
    @command("exploding_payload")
    async def cmd_exploding_payload(context: Context):
        # This is here only to create an exception once triggered by the on_message method.
        raise NotImplementedError("This message is expected during testing.")

    result = await bot_fx.on_message("#pytesting", "SomeUser", "!exploding_payload")

    assert result is None
    assert bot_fx.sent_messages
