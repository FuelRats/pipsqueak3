"""
test_mechaclient.py - tests for src.mechaclient class

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
import pytest
from src.mechaclient import MechaClient
from src.packages.fact_manager import FactManager

pytestmark = pytest.mark.mechaclient


def test_verify_version(bot_fx):
    """
    Asserts the version is set, and returning string.
    """
    assert bot_fx.__version__
    assert isinstance(bot_fx.__version__, str)


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
    Asserts the api_handler property returns an object, and cannot be set (no setter)
    """
    # Helper Class
    class FakeAPIHandler:
        ...

    assert bot_fx.api_handler is None

    with pytest.raises(AttributeError):
        bot_fx.api_handler = FakeAPIHandler()


def test_verify_fact_manager(bot_fx):
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
    assert isinstance(bot_fx.fact_manager, FakeFactManager)

    with pytest.raises(TypeError):
        bot_fx.fact_manager = "Something that isn't a Fact Manager"

