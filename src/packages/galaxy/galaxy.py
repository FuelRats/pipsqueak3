"""
galaxy.py - Provide functions to interact with and retrieve useful information from the
            Fuel Rats Systems API.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import asyncio
import json
import typing
from html import escape

import aiohttp

from src.config import CONFIG_MARKER
from .star_system import StarSystem
from ..utils import Vector


class Galaxy:
    """
    Worker class to interface with the Fuel Rats Systems API.
    """
    _config: typing.ClassVar[typing.Dict]

    @classmethod
    @CONFIG_MARKER
    def rehash_handler(cls, data: typing.Dict):
        """
        Apply new configuration data

        Args:
            data (typing.Dict): new configuration data to apply.

        """
        cls._config = data

    MAX_PLOT_DISTANCE = 20000

    MAX_RETRIES = 3
    "The maximum number of times to retry a failed HTTP request before failing permanently."

    TIMEOUT = aiohttp.ClientTimeout(total=10)
    "A ClientTimeout object representing the total time an HTTP request can take before failing."

    def __init__(self, url: str = None):
        self.url = url or self._config['system_api']['url']

    async def find_system_by_name(self,
                                  name: str,
                                  full_details: bool = False) -> typing.Optional[StarSystem]:
        """
        Finds a single system by its name and return its StarSystem object

        Args:
            name (str): The name of the system to search for.
            full_details (bool): Specify whether to simply find the correct system name
                or to retrieve all relevant details about a system (coordinates, spectral class,
                etc.)

        Returns:
            A ``StarSystem`` object representing the found system, or ``None`` if none was found.
        """

        data = await self._call("api/systems", {
            "filter[name:ilike]": name,
            "sort": "name",
            "limit": 1
        })
        print(data)
        if 'data' in data and data['data']:
            if full_details:
                return await self.find_system_by_id(data['data'][0]['id'])
            else:
                return StarSystem(name=data['data'][0]['attributes']['name'])

    async def find_system_by_id(self, system_id: int) -> typing.Optional[StarSystem]:
        """
        Finds a single system by its ID and returns its StarSystem object.

        Args:
            system_id (int): The ID of the system to search for.

        Returns:
            A ``StarSystem`` object representing the found system, or ``None`` if none was found.
        """

        data = await self._call(f"api/systems/{system_id}")
        if 'data' in data and data['data']:
            sys = data['data']['attributes']
            main_star = await self._find_main_star(system_id)
            sys['spectral_class'] = main_star['spectral_class'] if main_star is not None else None
            return StarSystem(position=Vector(**sys['coords']),
                              name=sys['name'],
                              spectral_class=sys['spectral_class'])

    async def _find_main_star(self, system_id: int) -> typing.Optional[typing.Dict]:
        """
        Find the main star of a system given its system ID.

        Args:
            system_id (int): The ID of the system, given from the Systems API.

        Returns:
            If found, returns a dict containing the information about the main star, matching the
            structure of the data returned from the /api/stars endpoint.
            If the system given cannot be found, returns None.
        """

        stars = await self._call("api/stars", {"filter[systemId64:eq]": system_id})
        for star in stars['data']:
            if star['attributes']['isMainStar']:
                result = star['attributes']
                result['id'] = star['id']
                result['spectral_class'] = star['attributes']['subType'][0]
                return result

    async def find_nearest_landmark(self,
                                    system: StarSystem
                                    ) -> typing.Optional[typing.Tuple[StarSystem, float]]:
        """
        Find the nearest "landmark" system to the one provided.

        Args:
            system (StarSystem): The system to center the search around.

        Returns:
            A tuple containing the landmark StarSystem closest to the one provided, and a float
            value indicating the distance between the two.
            May return None if the provided system is not found, or
            in the case of an API failure.
        """

        found_system = await self.find_system_by_name(system.name)
        if found_system is None:
            return None

        data = await self._call("landmark", {"name": found_system.name})
        if 'landmarks' in data and data['landmarks']:
            landmark = await self.find_system_by_name(data['landmarks'][0]['name'])
            return (landmark, round(data['landmarks'][0]['distance'], 2))

    async def search_systems_by_name(self, name: str) -> typing.Optional[typing.List[str]]:
        """
        Perform a fuzzy search for star systems on the name given to us.

        Args:
            name (str): The system name to search for.

        Returns:
            A list of up to 5 system names that closest match ``name``, or ``None`` if
            none could be found.
        """

        matches = await self._call("mecha", {"name": name.upper()})
        # Check to ensure the data set is not missing or empty.
        if 'data' in matches and matches['data']:
            return [match['name'] for match in matches['data']]

    async def _retry_delay(self, current_retry: int) -> None:
        """
        Uses asyncio.sleep to pause execution for a number of seconds equal to
        `current_retry` squared.
        """
        await asyncio.sleep(current_retry ** 2)

    async def _call(self,
                    endpoint: str,
                    params: typing.Optional[typing.Dict[str, str]] = None) -> typing.Union[dict, list]:
        """
        Perform an API call on the Fuel Rats Systems API.

        Args:
            endpoint (str): The API endpoint to request.
            params (typing.Dict): A dictionary of key-value pairs that will make up the query string.

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
