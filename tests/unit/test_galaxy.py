"""
test_galaxy.py - tests for the Galaxy API manager.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE
"""

import asyncio
import pytest

import aiohttp

pytestmark = [pytest.mark.unit, pytest.mark.galaxy]


@pytest.mark.asyncio
async def test_find_system_by_name(galaxy_fx):
    """
    Test that we can find a system by name and get the proper information.
    """
    system = await galaxy_fx.find_system_by_name("Angrbonii")
    assert system.position.x == 61.65625
    assert system.position.y == -42.4375
    assert system.position.z == 53.59375
    assert system.name == "ANGRBONII"
    assert system.spectral_class == "L"


@pytest.mark.asyncio
async def test_find_system_by_invalid_name(galaxy_fx):
    """
    Test that an invalid system will return None.
    """
    invalid = await galaxy_fx.find_system_by_name("Fualun")
    assert invalid is None


@pytest.mark.asyncio
async def test_find_nearest_landmark(galaxy_fx):
    """
    Test that we can find the nearest landmark from a provided system.
    """
    system = await galaxy_fx.find_system_by_name('Angrbonii')
    nearest = await galaxy_fx.find_nearest_landmark(system)
    assert nearest[0].name == 'FUELUM'
    assert nearest[1] == 14.56


@pytest.mark.asyncio
async def test_find_nearest_landmark_self(galaxy_fx):
    """
    Test that a trying to find the nearest landmark from a landmark system returns itself.
    """
    system = await galaxy_fx.find_system_by_name('Fuelum')
    nearest = await galaxy_fx.find_nearest_landmark(system)
    assert nearest[0].name == 'FUELUM'
    assert nearest[1] == 0


@pytest.mark.asyncio
async def test_find_nearest_landmark_invalid(galaxy_fx, monkeypatch):
    """
    Test that find_nearest_landmark will raise in the unlikely event it can't find
    a landmark.
    """
    system = await galaxy_fx.find_system_by_name('Angrbonii')
    monkeypatch.setattr(galaxy_fx, 'LANDMARK_SYSTEMS', {})
    with pytest.raises(RuntimeError):
        await galaxy_fx.find_nearest_landmark(system)


@pytest.mark.asyncio
async def test_search_systems_by_name(galaxy_fx):
    """
    Test that we can get a list of similar systems by name.
    """
    nearest = await galaxy_fx.search_systems_by_name("Fualun")
    assert 'Walun' in nearest


@pytest.mark.asyncio
async def test_search_systems_by_invalid_name(galaxy_fx):
    """
    Test that receiving no similar results for a system returns None.
    """
    invalid = await galaxy_fx.search_systems_by_name("!!!")
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

@pytest.mark.asyncio
@pytest.mark.parametrize("retry, seconds", ((1, 1), (2, 4), (3, 9)))
async def test_retry_delay(galaxy_fx, monkeypatch, async_callable_fx, retry: int, seconds: int):
    """
    Test that `retry_delay` calls the appropriate function to pause execution for the
    appropriate amount of time.
    """
    monkeypatch.setattr(asyncio, 'sleep', async_callable_fx)
    await galaxy_fx._retry_delay(retry)
    assert async_callable_fx.was_called
    assert async_callable_fx.was_called_with(seconds)

@pytest.mark.asyncio
async def test_http_retry_eventually(galaxy_fx, monkeypatch, async_callable_fx):
    """
    Test that Galaxy will retry a failed request a number of times before failing.
    Ensures that an eventually-good endpoint will return data.
    """
    monkeypatch.setattr(galaxy_fx, '_retry_delay', async_callable_fx)
    data = await galaxy_fx._call("badendpoint")
    assert data['success']

@pytest.mark.asyncio
async def test_http_retry_permanent(galaxy_fx, monkeypatch, async_callable_fx):
    """
    Test that Galaxy has a limit to number of retries before it will outright
    fail.
    """
    monkeypatch.setattr(galaxy_fx, '_retry_delay', async_callable_fx)
    with pytest.raises(aiohttp.ClientError):
        await galaxy_fx._call("reallybadendpoint")
