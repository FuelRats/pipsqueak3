"""
conftest.py - PyTest configuration and shared resources

Reusable test fixtures 'n stuff


Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""
from uuid import uuid4

import pytest

from Modules.rat_rescue import Rescue
from Modules.rats import Rats
from ratlib.names import Platforms


@pytest.fixture(params=[("pcClient", Platforms.PC, "firestone"),
                        ("xxXclient", Platforms.XB, "sol"),
                        ("psCoolKid", Platforms.PS, "NLTT 48288")],
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
    myRescue = Rescue(uuid4(), client=params[0], system=params[2], irc_nickname=params[0])
    myRescue.platform = params[1]
    return myRescue


@pytest.fixture
def RescuePlain_fx() -> Rescue:
    """
    A plain initialized Rescue without parametrization

    Returns:
        Rescue : Plain initialized Rescue
    """
    return Rescue(uuid4(), "UNIT_TEST", "ki", "UNIT_TEST")


@pytest.fixture
def RatNoID_fx():
    """
    Returns: (Rescue): Rescue test fixture without an api ID

    """
    return Rats(None, "noIdRat")


@pytest.fixture(params=[("myPcRat", Platforms.PC),
                        ("someXrat", Platforms.XB),
                        ("psRatToTheRescue", Platforms.PS)],
                scope='module')
def RatGood_fx(request) -> Rats:
    """
    Testing fixture containing good and registered rats
    """
    params = request.param
    myRat = Rats(uuid4(), name=params[0], platform=params[1])
    return myRat
