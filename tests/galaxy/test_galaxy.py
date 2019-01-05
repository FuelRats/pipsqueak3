"""
test_galaxy.py - tests for the Galaxy API manager.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""

import pytest

pytestmark = pytest.mark.galaxy


@pytest.mark.asyncio
async def test_find_system_by_name(galaxy_fx):
    """
    Test that we can find a system by name and get the proper information.
    """
    system = await galaxy_fx.find_system_by_name("Fuelum")
    assert system.position.x == 52.0
    assert system.position.y == -52.65625
    assert system.position.z == 49.8125
    assert system.name == "FUELUM"
    assert system.spectral_class == "K"
    assert system.is_populated


@pytest.mark.asyncio
async def test_find_system_by_invalid_name(galaxy_fx):
    """
    Test that an invalid system will return None.
    """
    invalid = await galaxy_fx.find_system_by_name("Fualun")
    assert invalid is None


@pytest.mark.asyncio
async def test_search_systems_by_name(galaxy_fx):
    """
    Test that we can get a list of similar systems by name.
    """
    nearest = await galaxy_fx.search_systems_by_name("Fualun")
    assert nearest[0] == 'FUELUM'
    assert nearest[1] == 'FOLNA'
    assert nearest[2] == 'FEI LIN'


@pytest.mark.asyncio
async def test_search_systems_by_invalid_name(galaxy_fx):
    """
    Test that receiving no similar results for a system returns None.
    """
    invalid = await galaxy_fx.search_systems_by_name("!")
    assert invalid is None


@pytest.mark.asyncio
async def test_plot_waypoint_route(galaxy_fx):
    """
    Test that we can successfully plot a route in 20kly increments.
    """
    route = await galaxy_fx.plot_waypoint_route("Fuelum", "Beagle Point")
    assert route[0] == 'FUELUM'
    assert route[1] == 'EORLD PRI QI-Z D1-4302'
    assert route[2] == 'PRAE FLYI RO-I B29-113'
    assert route[3] == 'CHUA EOHN CT-F D12-2'
    assert route[4] == 'BEAGLE POINT'


@pytest.mark.asyncio
async def test_plot_waypoint_route_nearby(galaxy_fx):
    """
    Test that plotting between two systems already within 20kly of each other other works.
    """
    route = await galaxy_fx.plot_waypoint_route("Fuelum", "Angrbonii")
    assert route[0] == 'FUELUM'
    assert route[1] == 'ANGRBONII'


@pytest.mark.asyncio
async def test_plot_waypoint_route_invalid(galaxy_fx):
    """
    Test that plotting an invalid route raises an exception.
    """
    with pytest.raises(ValueError):
        await galaxy_fx.plot_waypoint_route("Fuelum", "Fualun")
