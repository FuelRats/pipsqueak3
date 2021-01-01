"""
conftest.py - PyTest configuration and shared resources

Reusable test fixtures 'n stuff


Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
import logging
import random
import string
import sys
from typing import Dict, List
from uuid import uuid4, UUID

import psycopg2.pool
import pytest

# from psycopg2.pool import SimpleConnectionPool
from src.config import CONFIG_MARKER, PLUGIN_MANAGER, setup_logging, setup
from src.config.datamodel import ConfigRoot
from src.config.datamodel.api import FuelratsApiConfigRoot
from src.config.datamodel.gelf import GelfConfig
from src.packages import cli_manager
from src.packages.cache.rat_cache import RatCache

# Set argv to keep cli arguments meant for pytest from polluting our things
from src.packages.fuelrats_api.v3.interface import ApiV300WSS
from tests.fixtures.mock_websocket import FakeConnection, Expectation

sys.argv = ["test",
            "--config-file", "testing.toml",
            "--clean-log",
            "--verbose",
            ]

# Include other conftest files
pytest_plugins = ["tests.fixtures.galaxy_fx"]

setup_logging(
    "logs/unit_tests.log",
    gelf_configuration=GelfConfig(
        enabled=False, port=None, host="localhost"
    )
)

from src.packages.permissions.permissions import Permission
from tests.fixtures.mock_bot import MockBot
from src.packages.board import RatBoard
from src.packages.rescue import Rescue
from src.packages.rat import Rat
from src.packages.utils import Platforms, Status
from src.packages.context import Context
from src.packages.epic import Epic
from src.packages.user import User
from src.packages.mark_for_deletion.mark_for_deletion import MarkForDeletion
from tests.fixtures.mock_callables import CallableMock, AsyncCallableMock
from src.packages.database import DatabaseManager
from src.packages.fact_manager.fact import Fact
from src.packages.fuelrats_api.mockup.mockup import MockupAPI


@pytest.fixture(params=[("pcClient", Platforms.PC, "firestone", 24),
                        ("xxXclient", Platforms.XB, "sol", 2),
                        ("psCoolKid", Platforms.PS, "NLTT 48288", 33)],
                )
def rescue_sop_fx(request) -> Rescue:
    """
    A Rescue fixture providing Rescue objects for the 3 supported platforms

    Args:
        request (): Provided by fixture Parametrization

    Returns:
        Rescue : Rescue objects
    """
    params = request.param
    myRescue = Rescue(uuid4(), client=params[0], system=params[2], irc_nickname=params[0],
                      board_index=params[3])
    myRescue.platform = params[1]
    return myRescue


@pytest.fixture(params=(0, 1))
def rescues_fx(request, rescue_sop_fx, rescue_plain_fx):
    if request.param:
        return rescue_plain_fx
    return rescue_sop_fx


@pytest.fixture
def rescue_plain_fx() -> Rescue:
    """
    A plain initialized Rescue without parametrization

    Returns:
        Rescue : Plain initialized Rescue
    """
    return Rescue(uuid4(), "UNIT_TEST", "ki", "UNIT_TEST", board_index=42, status=Status.OPEN,
                  platform=Platforms.PC)


@pytest.fixture
def rat_no_id_fx():
    """
    Returns: (Rescue): Rescue test fixture without an api ID

    """
    return Rat(None, "noIdRat")


@pytest.fixture(params=[("myPcRat", Platforms.PC, UUID("dead4ac0-0000-0000-0000-00000000beef")),
                        ("someXrat", Platforms.XB, UUID("FEED000-FAC1-0000-0000900000D15EA5E")),
                        ("psRatToTheRescue", Platforms.PS,
                         UUID("FEE1DEA-DFAC-0000-000001BADB001FEED"))],
                )
def rat_good_fx(request) -> Rat:
    """
    Testing fixture containing good and registered rats
    """
    params = request.param
    rat = Rat(uuid=params[2], name=params[0], platform=params[1])
    RatCache().append(rat)
    return rat


@pytest.fixture(params=[("noIdRat", None, uuid4()),
                        ("myPcRat", Platforms.PC, uuid4()),
                        ("someXrat", Platforms.XB, uuid4()),
                        ("psRatToTheRescue", Platforms.PS, uuid4())],
                )
def rat_no_id_and_good_fx(request) -> Rat:
    """
    Testing fixture containing both good and registered rats, and also unregistered rats
    """
    params = request.param
    rat = Rat(uuid=params[2], name=params[0], platform=params[1])
    RatCache().append(rat)
    return rat


@pytest.fixture
def rat_board_fx() -> RatBoard:
    """
    Provides a RatBoard object

    Returns:
        RatBoard: initialized ratboard object
    """
    return RatBoard()


@pytest.fixture()
def bot_fx(configuration_fx, galaxy_fx):
    mock_bot = MockBot(nickname="mock_mecha3[BOT]", mecha_config=configuration_fx)
    mock_bot.galaxy = galaxy_fx
    return mock_bot


@pytest.fixture
def user_fx():
    return User(False,
                None,
                True,
                "unit_test",
                "unit_test[bot]",
                "unit_test",
                "unittest.rats.fuelrats.com",
                "potatobot"
                )


@pytest.fixture
def context_channel_fx(user_fx, bot_fx) -> Context:
    """
    Provides a context fixture

    Returns:
        Context
    """
    context = Context(bot_fx, user_fx, "#unit_test", ["my", "word"], ["my", "my word"])
    return context


@pytest.fixture
def context_pm_fx(user_fx, bot_fx) -> Context:
    """
    Provides a context fixture

    Returns:
        Context
    """
    context = Context(bot_fx, user_fx, "someUSer", ["my", "word"], ["my", "my word"])
    return context


@pytest.fixture(params=[0, 1])
def context_fx(request, bot_fx, user_fx):
    """Parametrized context fixture, returning a channel and non-channel Context object"""
    if request.param == 0:
        return Context(bot_fx, user_fx, "#unit_test", ["my", "word"], ["my", "my word"])
    elif request.param == 1:
        return Context(bot_fx, user_fx, "someUSer", ["my", "word"], ["my", "my word"])

    raise ValueError


@pytest.fixture
def logging_fx(caplog) -> logging.Logger:
    """
    Calls config.setup_logging with a test_log.log file for testing purposes.
    :return:
    """
    caplog.clear()
    return logging.getLogger("mecha.logging_fx")


@pytest.fixture
def spooled_logging_fx(caplog) -> logging.Logger:
    """
    Same as logging_fx, but under separate namespace for the logger to
    use a temporary file.
    """
    caplog.clear()
    return logging.getLogger("mecha.spooled_logging_fx")


@pytest.fixture
def random_string_fx() -> str:
    """
    Creates a 16 digit alphanumeric string.  For use
    with logging tests.

    Returns:
         16 digit alphanumeric string.
    """
    result = "".join(random.sample(string.ascii_letters, 16))
    return result


@pytest.fixture
def epic_fx(rescue_plain_fx, rat_good_fx) -> Epic:
    """Provides an Epic object fixture"""
    return Epic(uuid4(), "my notes package", rescue_plain_fx, rat_good_fx)


@pytest.fixture
def mark_for_deletion_plain_fx() -> MarkForDeletion:
    """Provides a plain MFD object"""
    return MarkForDeletion()


@pytest.fixture(params=[(True, 'White Sheets', 'Disallowable cut of jib'),
                        (False, 'Shatt', 'Not Enough Cowbell'),
                        (False, 'unkn0wn', 'Object in mirror appears too close')])
def mark_for_deletion_fx(request) -> MarkForDeletion:
    """Provides a parameterized MFD object"""
    param = request.param
    return MarkForDeletion(marked=param[0], reporter=param[1], reason=param[2])


@pytest.fixture
def rat_cache_fx():
    """provides a empty rat_cache"""
    return RatCache()


@pytest.fixture(autouse=True)
def reset_rat_cache_fx(rat_cache_fx: RatCache):
    """"cleans up the rat_cache's cache"""
    # ensure the cache is clean during setup
    rat_cache_fx.flush()
    yield
    # and clean up after ourselves
    rat_cache_fx.flush()


@pytest.fixture
def permission_fx(monkeypatch) -> Permission:
    """
    Provides a permission fixture

    Args:
        monkeypatch ():

    Returns:

    """
    # ensure _by_vhost is clean prior to running test
    monkeypatch.setattr("src.packages.permissions.permissions._by_vhost", {})
    permission = Permission(0, {"testing.fuelrats.com", "cheddar.fuelrats.com"})
    return permission


@pytest.fixture
def callable_fx():
    """
    Fixture providing a callable object whose return value can be set and which can be checked for
    having been called.

    See :class:`CallableMock`.
    """
    return CallableMock()


@pytest.fixture
def async_callable_fx():
    """
    Like :func:`callable_fx`, but can be treated as a coroutine function.

    See :class:`AsyncCallableMock`.
    """
    return AsyncCallableMock()


@pytest.fixture(scope="session")
def test_dbm_fx() -> DatabaseManager:
    """
    Test fixture for Database Manager.

    A DATABASE CONFIGURATION AND CONNECTION IS REQUIRED FOR THESE TESTS.
    """
    try:
        database = DatabaseManager()
    except psycopg2.DatabaseError:
        pytest.xfail("unable to instantiate database object, these tests cannot pass")
    return database


@pytest.fixture(scope="session")
def test_dbm_pool_fx(test_dbm_fx) -> psycopg2.pool.SimpleConnectionPool:
    """
    Test fixture for Database Manager's connection pool.

    A DATABASE CONFIGURATION AND CONNECTION IS REQUIRED FOR THESE TESTS.
    """
    return test_dbm_fx._dbpool


@pytest.fixture
def test_fact_empty_fx() -> Fact:
    return Fact("", "", [], "", "", "")


@pytest.fixture()
def test_fact_fx() -> Fact:
    return Fact(name='test',
                lang='en',
                message='This is a test fact.',
                aliases=['testfact'],
                author='Shatt',
                editedby='Shatt',
                mfd=False,
                edited=None
                )


class ConfigReceiver:
    """
    Namespace plugin for hooking into config events
    """
    data: ConfigRoot

    @classmethod
    @CONFIG_MARKER
    def rehash_handler(cls, data: ConfigRoot):
        cls.data = data


@pytest.fixture(scope="session", autouse=True)
def global_init_fx() -> None:
    """
    Session scoped auto-use plugin for loading CLI flags, configuration settings, and preparing
    the logging system.

    This fixture does not provide a value.
    """
    PLUGIN_MANAGER.register(ConfigReceiver, "testing_config_recv")
    # fetch the CLI argument
    _path = cli_manager.GET_ARGUMENTS().config_file
    # and initialize
    setup(_path)


@pytest.fixture(scope="session")
def configuration_fx() -> ConfigRoot:
    """
    provides the session configuration dictionary, as loaded at test session start.
    """
    return ConfigReceiver.data


@pytest.fixture
def mock_fuelrats_api_fx():
    # TODO pull from configuration system
    pytest.xfail("FIXME deprecated API ")
    return MockupAPI(url=r'http:///api')


@pytest.fixture
def board_online_fx(rat_board_fx, mock_fuelrats_api_fx):
    rat_board_fx._handler = mock_fuelrats_api_fx
    rat_board_fx._offline = False

    return rat_board_fx


@pytest.fixture(scope="function")
def api_wss_connection_fx() -> FakeConnection:
    """ The expectations `api_wss_fx` use, provided here for ease of access """
    return FakeConnection()


@pytest.fixture
def api_wss_fx(api_wss_connection_fx) -> ApiV300WSS:
    interface = ApiV300WSS(connection=api_wss_connection_fx, config=FuelratsApiConfigRoot(
        online_mode=False, uri="localhost", authorization=None
    ))
    interface.connected_event.set()
    yield interface
    assert not api_wss_connection_fx.expectations, "Unresolved expectations remain..."
