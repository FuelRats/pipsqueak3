"""
test_galaxy.py - tests for the Galaxy API manager.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""

import logging
import pytest

log = logging.getLogger(f"mecha.{__name__}")

pytestmark = pytest.mark.galaxy


@pytest.mark.asyncio
async def test_find_system_by_name(galaxy_fx, mock_api_server_fx):
    system = await galaxy_fx.find_system_by_name("Fuelum")
    assert system.position.x == 52.0
    assert system.position.y == -52.65625
    assert system.position.z == 49.8125
    assert system.name == "FUELUM"
    assert system.spectral_class == "K"
    assert system.is_populated

    # Test that an invalid system will return None.
    invalid = await galaxy_fx.find_system_by_name("Fualun")
    assert invalid is None


@pytest.mark.asyncio
async def test_search_systems_by_name(galaxy_fx):
    nearest = await galaxy_fx.search_systems_by_name("Fualun")
    assert nearest[0] == 'FUELUM'
    assert nearest[1] == 'FOLNA'
    assert nearest[2] == 'FEI LIN'

    # Test that receiving no similar results for a system returns None.
    invalid = await galaxy_fx.search_systems_by_name("!")
    assert invalid is None


@pytest.mark.asyncio
async def test_plot_waypoint_route(galaxy_fx):
    route = await galaxy_fx.plot_waypoint_route("Fuelum", "Beagle Point")
    assert route[0] == 'FUELUM'
    assert route[1] == 'EORLD PRI QI-Z D1-4302'
    assert route[2] == 'PRAE FLYI RO-I B29-113'
    assert route[3] == 'CHUA EOHN CT-F D12-2'
    assert route[4] == 'BEAGLE POINT'

    # Test that plotting between two systems already within 20kly of
    # each other other works.
    route = await galaxy_fx.plot_waypoint_route("Fuelum", "Angrbonii")
    assert route[0] == 'FUELUM'
    assert route[1] == 'ANGRBONII'

    # Test that plotting an invalid route returns None.
    invalid = await galaxy_fx.plot_waypoint_route("Fuelum", "Fualun")
    assert invalid is None


@pytest.mark.asyncio
async def test_find_nearest_scoopable(galaxy_fx):
    scoopable = await galaxy_fx.find_nearest_scoopable('Angrbonii')
    assert scoopable.name == 'CRUCIS SECTOR EW-N A6-0'

    # Test that an already scoopable star will return itself.
    scoopable = await galaxy_fx.find_nearest_scoopable('Fuelum')
    assert scoopable.name == 'FUELUM'

    # Test that an invalid system will return None.
    invalid = await galaxy_fx.find_nearest_scoopable('Fualun')
    assert invalid is None
