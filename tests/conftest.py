"""
conftest.py - PyTest configuration and shared resources

Reusable test fixtures 'n stuff


Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
from uuid import uuid4, UUID

import pytest

from tests.mock_bot import MockBot


def pytest_addoption(parser):
    """Hooks pytest's add_option """
    parser.addoption("--config-file", "--config", default="testing.json")


from config import setup

# have config setup at the beginning of testing

setup("testing.json")
from Modules.rat_board import RatBoard
from Modules.rat_rescue import Rescue
from Modules.rats import Rats

from ratlib.names import Platforms


@pytest.fixture(params=[("pcClient", Platforms.PC, "firestone", 24),
                        ("xxXclient", Platforms.XB, "sol", 2),
                        ("psCoolKid", Platforms.PS, "NLTT 48288", 33)],
                )
def RescueSoP_fx(request) -> Rescue:
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
def RescuePlain_fx() -> Rescue:
    """
    A plain initialized Rescue without parametrization

    Returns:
        Rescue : Plain initialized Rescue
    """
    return Rescue(uuid4(), "UNIT_TEST", "ki", "UNIT_TEST", board_index=42)


@pytest.fixture
def RatNoID_fx():
    """
    Returns: (Rescue): Rescue test fixture without an api ID

    """
    return Rats(None, "noIdRat")


@pytest.fixture(params=[("myPcRat", Platforms.PC, UUID("dead4ac0-0000-0000-0000-00000000beef")),
                        ("someXrat", Platforms.XB, UUID("FEED000-FAC1-0000-0000900000D15EA5E")),
                        ("psRatToTheRescue", Platforms.PS,
                         UUID("FEE1DEA-DFAC-0000-000001BADB001FEED"))],
                )
def RatGood_fx(request) -> Rats:
    """
    Testing fixture containing good and registered rats
    """
    params = request.param
    myRat = Rats(params[2], name=params[0], platform=params[1])
    return myRat


@pytest.fixture
def RatBoard_fx() -> RatBoard:
    """
    Provides a RatBoard object

    Returns:
        RatBoard: initialized ratboard object
    """
    return RatBoard()


@pytest.fixture
def bot_fx():
    return MockBot()
