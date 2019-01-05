"""
galaxy.py - Provide functions to interact with and retrieve useful information from the
            Fuel Rats Systems API.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from html import escape
import json
from typing import Dict, List, Optional

import aiohttp

from config import config
from utils.ratlib import Vector
from .star_system import StarSystem


class Galaxy:
    """
    Worker class to interface with the Fuel Rats Systems API.
    """

    MAX_PLOT_DISTANCE = 20000

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

        data = await self._call("systems", {"filter[name:like]": name.upper(), "include": "bodies"})
        result_count = data['meta']['results']['available']
        if result_count > 0:
            sys = data['data'][0]['attributes']
            bodies = data['included']
            for body in bodies:
                if self._match_main_star(sys['name'], body['attributes']['name']):
                    sys['spectral_class'] = body['attributes']['spectral_class']
            return StarSystem(position=Vector(sys['x'], sys['y'], sys['z']),
                              name=sys['name'],
                              is_populated=sys['is_populated'],
                              spectral_class=sys.get('spectral_class'))

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
                                    "type": "soundex",
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
            start (StarSystem): The system in which to begin our journey.
            end (StarSystem): The system which we're travelling towards.
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

    async def _find_nearest_systems(self,
                                    x: float,
                                    y: float,
                                    z: float,
                                    limit: int = 10) -> Optional[List[str]]:
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
                                    "limit": limit})
        if nearest['data']:
            return [neighbor['name'] for neighbor in nearest['data']]

    @staticmethod
    def _match_main_star(system_name: str, body_name: str) -> bool:
        """
        Attempts to match a star system's name with the actual name of its main star,
        case insensitively.

        Elite: Dangerous will append an "A" to a system's main star if the system contains
        more than one star. This method simplifies searching for both variations at once.

        Args:
            system_name (str): The name of the star system.
            body_name (str): The name of the stellar body.

        Returns:
            True if the stellar body's name matches the star system, or if it matches the
            naming convention for the main star in a system ("System_Name A"). False otherwise.
        """
        return (system_name.casefold() == body_name.casefold() or
                f"{system_name} A".casefold() == body_name.casefold())

    async def _call(self, endpoint: str, params: Dict[str, str]) -> object:
        """
        Perform an API call on the Fuel Rats Systems API.

        Args:
            endpoint (str): The API endpoint to request.
            params (Dict): A dictionary of key-value pairs that will make up the query string.

        Returns:
            An object representing the parsed JSON data returned from the API endpoint.
        """

        base_url = self.url
        param_string = "?"
        if params:
            for key, value in params.items():
                param_string += f"{key}={escape(str(value))}&"
        url = f"{base_url}{endpoint}{param_string}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return json.loads(await(response.text()))
