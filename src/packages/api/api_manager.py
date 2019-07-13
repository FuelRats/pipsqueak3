"""
api_manager.py - Provide functions for communicating with the Fuel Rats API.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import asyncio
from datetime import datetime
import logging
import json
import typing
from urllib.parse import urlencode
from uuid import UUID

import aiohttp

from src.config import CONFIG_MARKER
from src.packages.mark_for_deletion import MarkForDeletion
from src.packages.rat import Rat
from src.packages.quotation import Quotation
from src.packages.rescue import Rescue
from src.packages.utils import Platforms, Status

LOG = logging.getLogger(f"mecha.{__name__}")


class APIManager:
    """
    Worker class to interface with the Fuel Rats API.
    """
    _config: typing.ClassVar[typing.Dict]
    _base_url: typing.ClassVar[str]
    _online_mode: typing.ClassVar[bool]
    MAX_RETRIES: typing.ClassVar[int] = 3
    TIMEOUT: typing.ClassVar[aiohttp.ClientTimeout] = aiohttp.ClientTimeout(total=10)

    @classmethod
    @CONFIG_MARKER
    def rehash_handler(cls, data: typing.Dict):
        """
        Apply new configuration data

        Args:
            data (Dict): New configuration data
        """
        cls._config = data
        cls._base_url = data['api']['url']
        cls._online_mode = data['api']['online_mode']
        if not cls._base_url.endswith('/'):
            cls._base_url = f"{cls._base_url}/"

    @classmethod
    @CONFIG_MARKER
    def validate_config(cls, data: typing.Dict):
        """
        Validate the API's configuration values.

        Args:
            data (Dict): Configuration options
        """
        if 'api' not in data:
            raise ValueError("[API] Config section 'api' could not be found!")

        api_data = data['api']

        if not isinstance(api_data['url'], str):
            raise ValueError("[API] API 'url' value must be a string.")

        if not isinstance(api_data['online_mode'], bool):
            raise ValueError("[API] API 'online_mode' must be true or false.")

        if not api_data['url'].startswith('http'):
            raise ValueError("[API] API 'url' must be a valid URL.")

    @staticmethod
    def parse_api_datetime(iso8601: str) -> datetime:
        """
        Parse the ISO8601 datetime string from the API into a python datetime object.
        """
        return datetime.strptime(iso8601, '%Y-%m-%dT%H:%M:%S.%f%z')

    @staticmethod
    def _set_by_path(base_object: typing.Dict,
                     path: str,
                     value: typing.Optional[object] = None) -> typing.Dict:
        """
        Update a Dict with the value given, using the path to identify what value to update.

        Example:
            >>>> my_dict = {'foo': {'bar': {'baz': 'qux'}}}
            >>>> my_dict = _set_by_path(my_dict, 'foo.bar.baz', 'zim')
            >>>> my_dict
            {'foo': {'bar': {'baz': 'zim'}}}

        Args:
            base_object (Dict): The object you want to modify.
            path (str): A string path indicating the 'path' to the object you want to update.
                        Separate nested dicts with a period.
            value (object): The new value to apply to the object at 'path'.

        Returns:
            A Dict with the requested change made, and all other elements left alone.
        """
        if not path:
            raise ValueError("No path given")
        paths = path.split(".")
        full_object = base_object
        final_index = len(paths) - 1
        data = full_object
        for i, element in enumerate(paths, 0):
            # If this is the end of the path, update the object with the new value.
            if i == final_index:
                data[element] = value
            else:
                # For nested dicts, initialize any dicts that don't already exist.
                if element not in data:
                    data[element] = {}
            data = data[element]
        return full_object

    @staticmethod
    def _serialize_rescue(rescue: Rescue,
                          attr_filter: typing.Optional[typing.Set[str]] = None) -> typing.Dict:
        """
        Serialize a Rescue object into a Dict that follows the JSONAPI format.

        Args:
            rescue (Rescue): The Rescue object to serialize.

        Returns:
            A Dict containing the data from the Rescue, in JSONAPI format.
        """
        # Associate each Rescue attribute with a 'path' in the JSON object.
        # The value can either be a string with the JSON path, or a tuple
        # with the JSON path and the value to serialize.
        # If given only the JSON path, it will automatically grab the value
        # from the rescue object.
        maps = {
            'api_id': ('id', f"{rescue.api_id}"),
            'client': 'attributes.client',
            'code_red': 'attributes.codeRed',
            'platform': ('attributes.platform', rescue.platform.name.casefold()),
            'status': ('attributes.status', rescue.status.name.casefold()),
            'system': 'attributes.system',
            'title': 'attributes.title',
            'outcome': 'attributes.outcome',
            'unidentified_rats': 'attributes.unidentifiedRats',
            'lang_id': ('attributes.data.langID', rescue.lang_id.casefold()),
            'irc_nickname': 'attributes.data.IRCNick',
            'board_index': 'attributes.data.boardIndex',
            # Not sure what this attribute is, but we'll include it anyway.
            'data_status': ('attributes.data.status', {}),
            'quotes': ('attributes.quotes', [
                {'author': quote.author,
                 'message': quote.message,
                 'createdAt': quote.created_at.astimezone().isoformat(),
                 'updatedAt': quote.updated_at.astimezone().isoformat(),
                 'lastAuthor': quote.last_author}
                for quote in rescue.quotes
            ]),
            'marked_for_deletion': ('attributes.data.markedForDeletion',
                                    {'marked': rescue.marked_for_deletion.marked,
                                     'reason': rescue.marked_for_deletion.reason,
                                     'reporter': rescue.marked_for_deletion.reporter
                                     }
                                    ),
            'rats': ('relationships.rats.data',
                     [{'type': 'rats', 'id': f"{rat.uuid}"} for rat in rescue.rats]),
            'first_limpet': ('relationships.firstLimpet.data',
                             {'type': 'rats',
                              'id': f"{rescue.first_limpet}"} if rescue.first_limpet else None)
        }

        if attr_filter is None:
            # If we were not given a filter, just serialize everything.
            attr_filter = set(maps.keys())
        else:
            # We can't send only part of the data object to the API. So, if even one attribute
            # of it is changed, we must serialize the entire data object.
            data_attribs = ['lang_id',
                            'data_status',
                            'irc_nickname',
                            'board_index',
                            'marked_for_deletion']
            for attrib in data_attribs:
                if attrib in attr_filter:
                    for data_attrib in data_attribs:
                        attr_filter.add(data_attrib)
                    break

        rescue_json = {}
        for attrib in attr_filter:
            # Make sure the attribute we're about to serialize actually has a mapping.
            if attrib in maps.keys():
                mapping = maps[attrib]
                path = ''
                value = None
                # If the value is just a string, grab the value from the Rescue object.
                if isinstance(mapping, str):
                    path = mapping
                    value = getattr(rescue, attrib)
                # Otherwise, it's a tuple, and the value is the second element.
                else:
                    path, value = mapping
                rescue_json = APIManager._set_by_path(rescue_json, path, value)

        rescue_json['type'] = 'rescues'
        return rescue_json

    @staticmethod
    def _deserialize_rat(data: typing.Dict) -> Rat:
        return Rat(UUID(data['id']),
                   data['attributes']['name'],
                   Platforms[data['attributes']['platform'].upper()])

    @staticmethod
    def _deserialize_rescue(data: typing.Dict,
                            included: typing.Optional[typing.Dict] = None) -> Rescue:
        """
        Deserialize a JSONAPI rescue into a Rescue object.

        Args:
            data (Dict): The "data" attribute of the JSON response. Should be an
                         object containing only one Rescue.
            included (Dict): The "included" attribute of the JSON response. If given,
                             the method will attempt to add Rat and first_limpet associations
                             to the returned Rescue object.

        Returns:
            A Rescue object representing the data given from JSONAPI.
        """
        attr = data['attributes']
        mfd = MarkForDeletion(attr['data']['markedForDeletion']['marked'],
                              attr['data']['markedForDeletion']['reporter'],
                              attr['data']['markedForDeletion']['reason'])
        quotes = [Quotation(quote['message'],
                            quote['author'],
                            APIManager.parse_api_datetime(quote['createdAt']),
                            APIManager.parse_api_datetime(quote['updatedAt']),
                            quote['lastAuthor'])
                  for quote in attr['quotes']]
        rats = []
        if included:
            for include in included:
                if include['type'] != 'rats':
                    continue
                rats.append(Rat(UUID(include['id']),
                                include['attributes']['name'],
                                Platforms[include['attributes']['platform'].upper()]))
        first_limpet = None
        if data['relationships']['firstLimpet']['data']:
            first_limpet = data['relationships']['firstLimpet']['data']['id']
        rescue = Rescue(
            uuid=UUID(data['id']),
            client=attr['client'],
            code_red=attr['codeRed'],
            lang_id=attr['data']['langID'],
            irc_nickname=attr['data']['IRCNick'],
            board_index=attr['data']['boardIndex'],
            mark_for_deletion=mfd,
            platform=Platforms[attr['platform'].upper()],
            quotes=quotes,
            status=Status[attr['status'].upper()],
            system=attr['system'],
            title=attr['title'],
            unidentified_rats=attr['unidentifiedRats'],
            rats=rats,
            first_limpet=first_limpet,
            created_at=APIManager.parse_api_datetime(attr['createdAt']),
            updated_at=APIManager.parse_api_datetime(attr['updatedAt'])
        )
        # rescue.outcome = attr['outcome']  # @TODO Needs a setter or something...
        return rescue

    def __init__(self, config: typing.Optional[typing.Dict]):
        if config:
            self.rehash_handler(config)

    async def get_rescue(self, uuid: str) -> Rescue:
        """
        Use the API to get a rescue by UUID.

        Args:
            uuid (str): The Rescue's UUID.

        Returns:
            A Rescue object describing the Rescue found, or None if none was found.
        """
        if not uuid:
            raise ValueError("uuid must be specified!")

        try:
            data = await self._call(f"rescues/{uuid}", {'include': 'rats'})
            if data['data']:
                return self._deserialize_rescue(data['data'], data['included'])
        except aiohttp.ClientError:
            return None

    async def create_rescue(self, rescue: Rescue):
        """
        Create the case in the API.

        Args:
            rescue (Rescue): The Rescue object to create in the API.
        """
        data = APIManager._serialize_rescue(rescue)
        del data['id']
        if data['relationships']['firstLimpet']['data'] is None:
            del data['relationships']['firstLimpet']
        jsonapi_data = {'data': data}
        new_rescue = await self._call('rescues', method='POST', body=jsonapi_data)
        return APIManager._deserialize_rescue(new_rescue)

    async def update_rescue(self, rescue: Rescue):
        """
        Update the case in the API with the data from new_data.

        Args:
            rescue (Rescue): The Rescue object to update in the API.
        """
        data = APIManager._serialize_rescue(rescue)
        jsonapi_data = {'data': data}
        await self._call(f"rescues/{rescue.api_id}", method='PATCH', body=jsonapi_data)

    # @TODO: @functools.lru_cache()
    async def get_rat(self, uuid: str) -> typing.Optional[Rat]:
        """
        Use the API to get a rat by UUID.

        Args:
            uuid (str): The Rat's UUID.

        Returns:
            A Rat object describing the Rat found, or None if none was found.

        Raises:
            ValueError: If uuid is not given.
        """
        if not uuid:
            raise ValueError("uuid must be specified!")

        try:
            data = await self._call(f"rats/{uuid}")
            return APIManager._deserialize_rat(data['data'])
        except aiohttp.ClientError:
            return None

    async def find_rat(self,
                       name: str,
                       platform: typing.Optional[Platforms] = None) -> typing.Optional[Rat]:
        """
        Use the API to find a rat by name, and optionally platform.

        Args:
            name (str): The Rat's name.
            platform (Platforms): The Rat's platform.

        Returns:
            A RatData object describing the Rat found, or None if none was found.
        """
        if not name:
            raise ValueError("name must be specified!")

        params = {'filter[name:ilike]': name}
        if platform:
            params['filter[platform:eq]'] = platform.name.casefold()

        try:
            data = await self._call('rats', params)
            if data:
                return APIManager._deserialize_rat(data['data'][0])
        except aiohttp.ClientError:
            return None

    async def _call(self,
                    endpoint: str,
                    params: typing.Optional[typing.Dict[str, str]] = None,
                    method: typing.Optional[str] = "GET",
                    body: typing.Optional[typing.Dict] = None
                    ) -> typing.Optional[typing.Union[dict, list]]:
        """
        Perform an API call on the Fuel Rats API.

        Args:
            endpoint (str): The API endpoint to request.
            params (Dict): A dictionary of key-value pairs that will make up the query string.
            method (str): The HTTP method to use for the API call.
            body (Dict): The body of the request. (For HTTP POST/PATCH/PUT)

        Returns:
            A dict or list object representing the parsed JSONAPI data returned.
            Returns None if in offline mode or the request fails.
        """

        if not self._online_mode:
            LOG.debug(f"API call to {endpoint} was requested, but we're in offline mode.")
            return None

        base_url = self._base_url
        param_string = urlencode(params or {})
        url = f"{base_url}{endpoint}?{param_string}"
        for retry in range(self.MAX_RETRIES):
            try:
                return json.loads(await self._perform_http(url, method, body))
            except aiohttp.ClientError:
                # Even if it errors, do not retry POST or PATCH requests multiple times.
                if retry == (self.MAX_RETRIES - 1) or method != 'GET':
                    raise
                await asyncio.sleep(retry ** 2)

    async def _perform_http(self,
                            uri: str,
                            method: str = 'GET',
                            body: typing.Optional[typing.Dict] = None) -> str:
        """
        Perform an HTTP request to the URI given, using the HTTP method provided.
        If method is POST, PUT, or PATCH, also send the body provided.

        Args:
            uri (str): The URI to request.
            method (str): The HTTP method to use when requesting.
            body (Dict): The body to include in POST/PUT/PATCH requests.

        Returns:
            A string containing the HTTP response.

        Raises:
            aiohttp.ClientError if the HTTP request fails.
        """
        http_headers = {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json',
            'User-Agent': 'MechaSqueak/3.0.0a'  # @TODO Use actual MechaClient version
        }
        async with aiohttp.ClientSession(raise_for_status=True,
                                         timeout=self.TIMEOUT,
                                         headers=http_headers) as session:
            if method == 'GET':
                async with session.get(uri) as response:
                    return await response.text()
            elif method == 'POST':
                async with session.post(uri, json=body) as response:
                    return await response.text()
            elif method == 'PATCH':
                async with session.patch(uri, json=body) as response:
                    return await response.text()
