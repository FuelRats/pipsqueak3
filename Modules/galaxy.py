"""
galaxy.py - Interface for the Fuel Rats Systems API

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from config import config
from html import escape
import json
import logging
from Modules.star_system import StarSystem
from typing import Dict

import aiohttp

log = logging.getLogger(f"mecha.{__name__}")


class Galaxy:
    """
    Worker class to interface with the Fuel Rats Systems API.
    """

    MAX_PLOT_DISTANCE = 20000

    def __init__(self, url: str = None):
        self.url = url or config['api'].get('url')

    async def find_system_by_name(self, name: str):
        """
        Finds a single system by its name and return its StarSystem object
        """

        data = await self._call("systems",
                                {"filter[name:like]": name.upper(),
                                 "include": "bodies"})
        result_count = data['meta']['results']['available']
        if result_count > 0:
            sys = data['data'][0]['attributes']
            star_name = f"{sys['name']} A".upper()
            bodies = data['included']
            for body in bodies:
                if (body['attributes']['name'].upper() == sys['name'].upper() or
                    body['attributes']['name'].upper() == star_name):
                    sys['spectral_class'] = body['attributes']['spectral_class']
            return StarSystem.from_dict(sys)

    async def find_nearest_scoopable(self, name: str) -> 'StarSystem':
        """
        Find the nearest fuel-scoopable star from the system given to us.
        """

        scoopables = ['K', 'G', 'B', 'F', 'O', 'A', 'M']
        system = await self.find_system_by_name(name)
        if system is None:
            return None
        if system.spectral_class in scoopables:
            return system

        data = await self._call("nearest",
                                {"x": system.position.x,
                                 "y": system.position.y,
                                 "z": system.position.z,
                                 "aggressive": 1,
                                 "limit": 50,
                                 "include": 1})

        for candidate in data['candidates']:
            star_name = f"{candidate['name']} A".upper()
            for body in data['included']['bodies']:
                body_name = body['name'].upper()
                if body_name == candidate['name'].upper() or body_name == star_name:
                    if body['spectral_class'] in scoopables:
                        return await self.find_system_by_name(candidate['name'])

    async def search_systems_by_name(self, name: str) -> list:
        """
        Perform a fuzzy (Soundex) search for star systems on the name given to us.
        Returns the top 10 results.
        """

        matches = await self._call("search",
                                   {"name": name.upper(),
                                    "type": "soundex",
                                    "limit": "5"})
        matched_systems = []
        if matches['data']:
            for match in matches['data']:
                matched_systems.append(match['name'])
            return matched_systems

    async def plot_waypoint_route(self,
                                  start: str,
                                  end: str,
                                  interval: int = MAX_PLOT_DISTANCE):
        """
        Plot a route of waypoints between two faraway systems. Distance between
        waypoints should not exceed "interval" light-years.
        """

        start_system = await self.find_system_by_name(start)
        end_system = await self.find_system_by_name(end)
        if start_system is None or end_system is None:
            return None
        # Because our "nearest system" calculations will be
        # calculated based off a cubic search, give us some wiggle room
        # because the corners of the cube will have a higher distance
        # than expected.
        interval *= 0.98

        route = [start_system]
        remaining_distance = start_system.distance(end_system)
        next_system = start_system
        while remaining_distance > interval:
            next_system = await self._furthest_between(next_system,
                                                       end_system,
                                                       interval)
            route.append(next_system)
            remaining_distance = next_system.distance(end_system)
        route.append(end_system)
        return list(map(lambda s: s.name, route))

    async def _furthest_between(self,
                                start: 'StarSystem',
                                end: 'StarSystem',
                                distance: int):
        """
        Finds the furthest star from away from "start" and towards "end",
        with a limitation of no more than "distance" light-years.
        """

        start_position = start.position
        end_position = end.position
        full_distance = start_position.distance(end_position)
        normal = (end_position - start_position).normal()
        new_position = start_position + (normal * distance)
        nearest = await self._find_nearest_systems(new_position.x,
                                                   new_position.y,
                                                   new_position.z)
        if nearest:
            return await self.find_system_by_name(nearest[0])

    async def _find_nearest_systems(self,
                                    x: int,
                                    y: int,
                                    z: int,
                                    limit: int = 10):
        """
        Given a set of galactic coordinates, find the closest star systems.
        """

        nearest = await self._call("nearest",
                                   {"x": x,
                                    "y": y,
                                    "z": z,
                                    "aggressive": "1",
                                    "limit": limit})
        systems = []
        if nearest['data']:
            for neighbor in nearest['data']:
                systems.append(neighbor['name'])
            return systems

    async def _call(self, endpoint: str, params: Dict[str, str]):
        """
        Perform an API call on the Fuel Rats Systems API.
        """

        base_url = self.url
        param_string = "?"
        if params:
            for key, value in params.items():
                param_string += f"{key}={escape(str(value))}&"
        url = f"{base_url}{endpoint}{param_string}"
        body = await self._get(url)
        data = json.loads(body)
        return data

    async def _get(self, uri: str):
        """
        Performs an HTTP GET request on the URI and returns the response body.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as response:
                return await response.text()
