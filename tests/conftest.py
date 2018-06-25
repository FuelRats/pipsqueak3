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
from uuid import uuid4, UUID

import pytest

# Set argv to keep cli arguments meant for pytest from polluting our things
sys.argv = ["test",
            "--config-file", "testing.json",
            "--clean-log",
            "--verbose",
            ]

# This import statement is where the config gets read
from config import setup_logging

setup_logging("logs/unit_tests.log")

from tests.mock_bot import MockBot
from Modules.rat_board import RatBoard
from Modules.rat_rescue import Rescue
from Modules.rats import Rats
from utils.ratlib import Platforms
from Modules.context import Context
from Modules.epic import Epic
from Modules.user import User
from Modules.mark_for_deletion import MarkForDeletion


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


@pytest.fixture
def rescue_plain_fx() -> Rescue:
    """
    A plain initialized Rescue without parametrization

    Returns:
        Rescue : Plain initialized Rescue
    """
    return Rescue(uuid4(), "UNIT_TEST", "ki", "UNIT_TEST", board_index=42)


@pytest.fixture
def rat_no_id_fx():
    """
    Returns: (Rescue): Rescue test fixture without an api ID

    """
    return Rats(None, "noIdRat")


@pytest.fixture(params=[("myPcRat", Platforms.PC, UUID("dead4ac0-0000-0000-0000-00000000beef")),
                        ("someXrat", Platforms.XB, UUID("FEED000-FAC1-0000-0000900000D15EA5E")),
                        ("psRatToTheRescue", Platforms.PS,
                         UUID("FEE1DEA-DFAC-0000-000001BADB001FEED"))],
                )
def rat_good_fx(request) -> Rats:
    """
    Testing fixture containing good and registered rats
    """
    params = request.param
    myRat = Rats(params[2], name=params[0], platform=params[1])
    return myRat


@pytest.fixture
def rat_board_fx() -> RatBoard:
    """
    Provides a RatBoard object

    Returns:
        RatBoard: initialized ratboard object
    """
    return RatBoard()


@pytest.fixture
def bot_fx():
    return MockBot()


@pytest.fixture
def user_fx():
    return User(False,
                0,
                False,
                None,
                True,
                True,
                "unit_test",
                "unit_test[bot]",
                "unit_test",
                "unittest.rats.fuelrats.com",
                "potatobot",
                "irc.fuelrats,com")


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
    return MarkForDeletion(False)


@pytest.fixture(params=[(True, 'White Sheets', 'Disallowable cut of jib'),
                        (False, 'Shatt', 'Not Enough Cowbell'),
                        (False, 'unkn0wn', 'Object in mirror appears too close')])
def mark_for_deletion_fx(request) -> MarkForDeletion:
    """Provides a parameterized MFD object"""
    param = request.param
    return MarkForDeletion(marked=param[0], reporter=param[1], reason=param[2])
