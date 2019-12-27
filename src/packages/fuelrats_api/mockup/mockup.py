import typing
from json import dumps
from uuid import UUID

import aiohttp
import attr
from loguru import logger

from src.packages.rat import Rat
from src.packages.rescue import Rescue
from ._converters import RatConverter, RescueConverter
from src.packages.fuelrats_api._base import FuelratsApiABC


class ApiError(RuntimeError):
    ...


@attr.s
class MockupAPI(FuelratsApiABC):
    # name overrides
    rat_converter = RatConverter
    rescue_converter = RescueConverter

    # post init behaviors
    def __attrs_post_init__(self):
        self.RAT_ENDPOINT = f"{self.url}/rats"
        self.RESCUE_ENDPOINT = f"{self.url}/rescues"

    # internals
    @staticmethod
    async def _query(method: str, query: str, **kwargs) -> typing.Dict:
        """
        Invoke API request

        Args:
            method: HTTP method
            query:  HTTP endpoint + parameters
            **kwargs:  kwargs passed to underlying Aiohttp query

        Returns:
            API response

        Raises:
            ApiError: non-2xx response code received
        """
        logger.debug("[{method}] {query}", method=method, query=query)
        async with aiohttp.ClientSession() as session:
            async with session.request(method=method, url=query, **kwargs) as response:
                data = await response.json()
                logger.debug("api response := {}", data)
                if response.status < 200 or response.status >= 300:
                    raise ApiError(response.status)
                return data

    # interface implementation

    async def get_rescues(self) -> typing.List[Rescue]:
        query = self.RESCUE_ENDPOINT

        json = await self._query(method="GET", query=query)
        # json will be a list of API rescue objects.
        # Parse this into our internal representation.
        return [self.rescue_converter.from_api(item) for item in json]

    async def get_rescue(self, uuid: UUID) -> Rescue:
        query = f"{self.RESCUE_ENDPOINT}/{uuid}"
        json = await self._query(method="GET", query=query)
        return self.rescue_converter.from_api(json)

    async def update_rescue(self, rescue: Rescue) -> typing.Dict:
        query = f"{self.RESCUE_ENDPOINT}/{rescue.api_id}"
        data = self.rescue_converter.to_api(rescue)
        logger.debug("update data := {}", data)
        return await self._query(
            method="PATCH", query=query, data=dumps(data), skip_auto_headers={"CONTENT-TYPE"},
        )

    async def get_rat(self, key: typing.Union[UUID, str]) -> Rat:
        if isinstance(key, UUID):
            query = f"{self.RAT_ENDPOINT}/{key}"
            json = await self._query(method="GET", query=query)
        elif isinstance(key, str):
            query = f"{self.RAT_ENDPOINT}?filter=[name:eq]={key}"
            json = await self._query(method="GET", query=query)

        else:
            raise TypeError(key)

        return self.rat_converter.from_api(json)

    async def create_rescue(self, rescue: Rescue) -> Rescue:
        payload = self.rescue_converter.to_api(rescue)

        # mock API doesn't allow client-generated IDs
        del payload["data"]["id"]

        query = f"{self.RESCUE_ENDPOINT}"
        response = await self._query(method="POST", query=query, json=payload)

        return self.rescue_converter.from_api(response)
