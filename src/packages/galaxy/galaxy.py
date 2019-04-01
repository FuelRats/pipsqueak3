"""
galaxy.py - Provide functions to interact with and retrieve useful information from the
            Fuel Rats Systems API.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import asyncio
from html import escape
import json
from typing import Dict, List, Optional, Tuple, Union

import aiohttp

from config import config
from ..utils import Vector
from .star_system import StarSystem


class Galaxy:
    """
    Worker class to interface with the Fuel Rats Systems API.
    """

    LANDMARK_SYSTEMS = {
        'beagle point': StarSystem(
            name='BEAGLE POINT',
            position=Vector(-1111.5625, -134.21875, 65269.75),
            spectral_class='K'
        ),
        'colonia': StarSystem(
            name='COLONIA',
            position=Vector(-9530.5, -910.28125, 19808.125),
            spectral_class='F'
        ),
        'fuelum': StarSystem(
            name='FUELUM',
            position=Vector(52, -52.65625, 49.8125),
            spectral_class='K'
        ),
        'rodentia': StarSystem(
            name='RODENTIA',
            position=Vector(-9530.53125, -907.25, 19787.375),
            spectral_class='M'
        ),
        'sagittarius a*': StarSystem(
            name='SAGITTARIUS A*',
            position=Vector(25.21875, -20.90625, 25899.96875),
            spectral_class=None
        ),
        'sol': StarSystem(
            name='SOL',
            position=Vector.zero(),
            spectral_class='G'
        )
    }
    MAX_PLOT_DISTANCE = 20000

    MAX_RETRIES = 3
    "The maximum number of times to retry a failed HTTP request before failing permanently."

    TIMEOUT = aiohttp.ClientTimeout(total=10)
    "A ClientTimeout object representing the total time an HTTP request can take before failing."

    def __init__(self, url: str = None):
        self.url = url or config['api']['url']

    async def find_system_by_name(self, name: str) -> Optional[StarSystem]:
        """
        Finds a single system by its name and return its StarSystem object

        Args:
            name (str): The name of the system to search for.

        Returns:
            A ``StarSystem`` object representing the found system, or ``None`` if none was found.
        """

        if name.casefold() in self.LANDMARK_SYSTEMS:
            return self.LANDMARK_SYSTEMS[name.casefold()]

        data = await self._call("api/systems", {"filter[name:eq]": name.upper()})
        result_count = data['meta']['results']['available']
        if result_count > 0:
            system_id = data['data'][0]['id']
            sys = data['data'][0]['attributes']
            main_star = await self._find_main_star(system_id)
            sys['spectral_class'] = main_star['spectral_class'] if main_star is not None else None
            return StarSystem(position=Vector(**sys['coords']),
                              name=sys['name'],
                              spectral_class=sys['spectral_class'])

    async def _find_main_star(self, system_id: int) -> Optional[Dict]:
        """
        Find the main star of a system given its system ID.

        Args:
            system_id (int): The ID of the system, given from the Systems API.

        Returns:
            If found, returns a dict containing the information about the main star, matching the
            structure of the data returned from the /api/stars endpoint.
            If the system given cannot be found, returns None.
        """

        stars = await self._call("api/stars", {"filter[systemId:eq]": system_id})
        for star in stars['data']:
            if star['attributes']['isMainStar']:
                result = star['attributes']
                result['id'] = star['id']
                result['spectral_class'] = star['attributes']['subType'][0]
                return result

    async def find_nearest_landmark(self, system: StarSystem) -> Tuple[StarSystem, float]:
        """
        Find the nearest "landmark" system to the one provided. A list of landmark systems
        can be found in Galaxy.LANDMARK_SYSTEMS.

        Args:
            system (StarSystem): The system to center the search around.

        Returns:
            A tuple containing the landmark StarSystem closest to the one provided, and a float
            value indicating the distance between the two.
        """

        if system.name.casefold() in self.LANDMARK_SYSTEMS:
            return (system, 0)

        closest_system = None
        closest_distance = -1
        for landmark in self.LANDMARK_SYSTEMS.values():
            distance = system.distance(landmark)
            if closest_distance == -1 or distance < closest_distance:
                closest_distance = round(distance, 2)
                closest_system = landmark

        if closest_system is None:
            # Something's gone terribly wrong, likely the LANDMARK_SYSTEMS dict is empty.
            raise RuntimeError(f"Could not find a closest landmark match for '{system.name}'!")

        return (closest_system, closest_distance)

    async def search_systems_by_name(self, name: str) -> Optional[List[str]]:
        """
        Perform a fuzzy (Soundex) search for star systems on the name
        given to us.

        Args:
            name (str): The system name to search for.

        Returns:
            A list of up to 10 system names that closest match ``name``, or ``None`` if
            none could be found.
        """

        matches = await self._call("search",
                                   {"name": name.upper(),
                                    "type": "dmeta",
                                    "limit": "5"})
        # Check to ensure the data set is not missing or empty.
        if matches['data']:
            return [match['name'] for match in matches['data']]

    async def plot_waypoint_route(self,
                                  start: str,
                                  end: str,
                                  interval: int = MAX_PLOT_DISTANCE) -> List[str]:
        """
        Plot a route of waypoints between two faraway systems. Distance between
        waypoints should not exceed "interval" light-years.

        Args:
            start (str): The system in which to begin our journey.
            end (str): The system which we're travelling towards.
            interval (int): The maximum distance between two waypoints, in light-years.

        Returns:
            A list of system names representing the route, starting with the start system and
            ending with the end system.

        Raises:
            ValueError: If either the start or end system cannot be found.
        """

        start_system = await self.find_system_by_name(start)
        end_system = await self.find_system_by_name(end)
        if start_system is None or end_system is None:
            raise ValueError("Invalid endpoints provided for the route!")
        # Because our "nearest system" calculations will be
        # calculated based off a cubic search, give us some wiggle room
        # because the corners of the cube will have a higher distance
        # than expected.
        interval *= 0.98

        route = [start_system]
        remaining_distance = start_system.distance(end_system)
        # To find our waypoint route:
        # Start in the starting system.
        next_system = start_system
        # Until we're less than 1 interval's distance away...
        while remaining_distance > interval:
            # Travel in the direction of our end system and find our next waypoint system.
            next_system = await self._furthest_between(next_system,
                                                       end_system,
                                                       interval)
            # Add the newest waypoint to our route...
            route.append(next_system)
            # And update the remaining distance to our goal.
            remaining_distance = next_system.distance(end_system)
        route.append(end_system)
        return [waypoint.name for waypoint in route]

    async def _furthest_between(self,
                                start: StarSystem,
                                end: StarSystem,
                                distance: int) -> Optional[StarSystem]:
        """
        Finds the furthest star from away from "start" and towards "end",
        with a limitation of no more than "distance" light-years.

        Args:
            start (StarSystem): The system to begin our journey in.
            end (StarSystem): The system which we want to head towards.
            distance (int): The maximum distance we can travel towards the end system.

        Returns:
            A ``StarSystem`` object representing the nearest star found after travelling
            ``distance`` light years from the start system towards the end system.

            Returns None if no system was found after travelling.
        """

        # Calculate the direction of travel required to go from ``start`` to ``end``.
        normal = (end.position - start.position).normal()
        # Travel in that direction for ``distance`` light years.
        new_position = start.position + (normal * distance)
        nearest = await self._find_nearest_systems(new_position.x,
                                                   new_position.y,
                                                   new_position.z)
        # Check to ensure the data set is not missing or empty.
        if nearest:
            return await self.find_system_by_name(nearest[0])

    async def _find_nearest_systems(self,     # pylint: disable=invalid-name
                                    x: float,
                                    y: float,
                                    z: float,
                                    limit: int = 10,
                                    cubesize: int = 50) -> Optional[List[str]]:
        """
        Given a set of galactic coordinates, find the closest star systems.

        Args:

            x (float): The galactic X coordinate to center the search on.
            y (float): The galactic Y coordinate to center the search on.
            z (float): The galactic Z coordinate to center the search on.
            limit (int): The maximum number of nearest systems to return.

        Returns:
            A ``list`` of ``StarSystem`` objects representing the nearest star systems, up to
            ``limit`` entries, or ``None`` if no nearby sysems could be found.
        """

        nearest = await self._call("nearest",
                                   {"x": x,
                                    "y": y,
                                    "z": z,
                                    "aggressive": "1",
                                    "limit": limit,
                                    "cubesize": cubesize})
        if nearest['data']:
            return [neighbor['name'] for neighbor in nearest['data']]

    async def _retry_delay(self, current_retry: int) -> None:
        """
        Uses asyncio.sleep to pause execution for a number of seconds equal to
        `current_retry` squared.
        """
        await asyncio.sleep(current_retry ** 2)

    async def _call(self,
                    endpoint: str,
                    params: Optional[Dict[str, str]] = None) -> Union[dict, list]:
        """
        Perform an API call on the Fuel Rats Systems API.

        Args:
            endpoint (str): The API endpoint to request.
            params (Dict): A dictionary of key-value pairs that will make up the query string.

        Returns:
            A dict or list object representing the parsed JSON data returned from the API endpoint.
        """

        base_url = self.url
        param_string = ""
        if params:
            param_string = '&'.join(
                [f"{key}={escape(str(value))}" for key, value in params.items()]
            )
        url = f"{base_url}{endpoint}?{param_string}"
        for retry in range(self.MAX_RETRIES):
            try:
                async with aiohttp.ClientSession(raise_for_status=True,
                                                 timeout=self.TIMEOUT) as session:
                    async with session.get(url) as response:
                        return json.loads(await response.text())
            except aiohttp.ClientError:
                # If we've used our last retry, re-raise the offending exception.
                if retry == (self.MAX_RETRIES - 1):
                    raise

                # Introduce a short pause between retries
                await self._retry_delay(retry)
