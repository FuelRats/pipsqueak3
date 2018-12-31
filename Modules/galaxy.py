"""
galaxy.py - Interface for the Fuel Rats Systems API

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from html import escape
import json
import logging
from math import sqrt
from typing import Dict

import aiohttp

log = logging.getLogger(f"mecha.{__name__}")


class Galaxy:
    async def find_nearest_scoopable(self, name: str):
        scoopables = ['K', 'G', 'B', 'F', 'O', 'A', 'M']
        system = await self._fetch_system(name)
        if system.spectral_class in scoopables:
            return (system, 0)
        nearest = await self._find_nearest_systems(system.x, system.y, system.z, 50)
        for neighbor in nearest:
            sys = await self._fetch_system(neighbor)
            if sys.spectral_class in scoopables:
                return (sys, round(system.distance_to(sys), 2))
        return None

    async def search_systems_by_name(self, name: str):
        matches = await self._fuzzy_fetch_systems(name)
        if matches is None:
            raise self.SystemNotFoundException
        return matches

    async def find_system_by_name(self, name: str):
        system = await self._fetch_system(name)
        if system is None:
            raise self.SystemNotFoundException
        return system

    async def plot_waypoint_route(self,
                                  start: str,
                                  end: str,
                                  interval: int = 20000):
        start_system = await self._fetch_system(start)
        end_system = await self._fetch_system(end)
        if start_system is None or end_system is None:
            raise self.SystemNotFoundException
        # Because our "nearest system" calculations will be
        # calculated based off a cubic search, give us some wiggle room
        # because the corners of the cube will have a higher distance
        # than expected.
        interval = interval * 0.98

        route = [start_system]
        remaining_distance = start_system.distance_to(end_system)
        next_system = start_system
        while remaining_distance > interval:
            next_system = await self._furthest_between(next_system,
                                                       end_system,
                                                       interval)
            route.append(next_system)
            remaining_distance = next_system.distance_to(end_system)
        route.append(end_system)
        return list(map(lambda s: s.name, route))

    async def _furthest_between(self, a: 'System', b: 'System', distance: int):
        log.info(f"Plotting route between {a.name} and {b.name} in {distance} increments")
        start_pos = self.Vector(a.x, a.y, a.z)
        end_pos = self.Vector(b.x, b.y, b.z)
        full_distance = start_pos.distance(end_pos)
        if full_distance <= distance:
            return b
        norm = (end_pos - start_pos).normal()
        new_pos = start_pos + (norm * distance)
        log.info(f"Traveled {distance}ly and ended up at {new_pos.x}, {new_pos.y}, {new_pos.z}")
        nearest = await self._find_nearest_systems(new_pos.x, new_pos.y, new_pos.z)
        log.info(f"Nearest systems are: {', '.join(nearest)}")
        if nearest is None:
            raise self.SystemNotFoundException
        return await self._fetch_system(nearest[0])

    async def _find_nearest_systems(self, x: int, y: int, z: int, limit: int = 10):
        nearest = await self._call(
            "nearest",
            {"x": x, "y": y, "z": z, "aggressive": "1", "limit": str(limit)})
        systems = []
        if nearest['data']:
            for neighbor in nearest['data']:
                systems.append(neighbor['name'])
            return systems
        return None

    async def _fuzzy_fetch_systems(self, name: str):
        matches = await self._call(
            "search",
            {"name": name.upper(), "type": "soundex", "limit": "5"})
        matched_systems = []
        if matches['data']:
            for match in matches['data']:
                matched_systems.append(match['name'])
            return matched_systems
        return None

    async def _fetch_system(self, name: str):
        data = await self._call(
            "systems",
            {"filter[name:like]": name.upper(), "include": "bodies"})
        result_count = data['meta']['results']['available']
        if result_count > 0:
            sys = data['data'][0]['attributes']
            star_name = f"{sys['name']} A".upper()
            bodies = data['included']
            for body in bodies:
                if (body['attributes']['name'].upper() == sys['name'].upper() or
                    body['attributes']['name'].upper() == star_name):
                    sys['spectral_class'] = body['attributes']['spectral_class']
            return self.System.from_dict(sys)

    async def _call(self, endpoint: str, params: Dict[str, str]):
        base_url = "https://system.api.fuelrats.com/"
        param_string = "?"
        if params:
            for key, value in params.items():
                param_string += f"{key}={escape(str(value))}&"
        url = f"{base_url}{endpoint}{param_string}"
        body = await self._get(url)
        data = json.loads(body)
        return data

    async def _get(self, uri: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as response:
                return await response.text()

    class Vector(object):
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z

        def magnitude(self):
            return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

        def normal(self):
            mag = self.magnitude()
            return Galaxy.Vector(self.x / mag, self.y / mag, self.z / mag)

        def distance(self, b):
            return sqrt(
                ((b.x - self.x) ** 2) +
                ((b.y - self.y) ** 2) +
                ((b.z - self.z) ** 2))

        def __add__(self, b):
            return Galaxy.Vector(self.x + b.x, self.y + b.y, self.z + b.z)

        def __sub__(self, b):
            return Galaxy.Vector(self.x - b.x, self.y - b.y, self.z - b.z)

        def __mul__(self, b):
            return Galaxy.Vector(self.x * b, self.y * b, self.z * b)

    class System(object):
        @classmethod
        def from_dict(cls, data: Dict):
            self = cls()
            self.x = data['x']
            self.y = data['y']
            self.z = data['z']
            self.name = data['name']
            self.spectral_class = data.get('spectral_class')
            self.is_populated = data.get('is_populated')
            return self

        def distance_to(self, b):
            return sqrt(
                ((b.x - self.x) ** 2) +
                ((b.y - self.y) ** 2) +
                ((b.z - self.z) ** 2))

    class SystemNotFoundException(Exception):
        pass
