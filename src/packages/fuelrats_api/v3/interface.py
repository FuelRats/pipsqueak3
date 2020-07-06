import typing
from uuid import UUID

import aiohttp
import attr
import json
from .models.v1.nickname import Nickname
from .._base import FuelratsApiABC
from ...rat import Rat
from ...rescue import Rescue
from prometheus_client import Histogram
from loguru import logger
import websockets
import asyncio
NICKNAME_TIME = Histogram(
    namespace="api",
    name="fetching_nicknames",
    unit="seconds",
    documentation="time spent retrieving nicknames...",
)


class ApiV300Rest(FuelratsApiABC):
    async def get_rescues(self) -> typing.List[Rescue]:
        pass

    async def get_rescue(self, key: UUID) -> typing.Optional[Rescue]:
        pass

    async def create_rescue(self, rescue: Rescue) -> Rescue:
        pass

    async def update_rescue(self, rescue: Rescue) -> None:
        pass

    async def get_rat(self, key: typing.Union[UUID, str]) -> Rat:
        pass

    def _call(self, query:str) -> asyncio.Future:
        ...

    async def find_nickname(self, key: str) -> Nickname:
        logger.trace("creating API session...")
        async with aiohttp.ClientSession(
            raise_for_status=True,
            timeout=aiohttp.ClientTimeout(total=5.0),
            headers={"authorization": self.authorization} if self.authorization else {},
        ) as session:
            logger.trace(f"requesting nick={key!r}")
            async with session.request(
                method="GET", url=f"{self.url}/nicknames?nick={key}"
            ) as response:
                data = await response.json()
                logger.trace("got response, decoding")
                nickname = Nickname.from_dict(data["data"][0])
                logger.debug(
                    f"retrieved nickname object {nickname.id!r} - {nickname.attributes.nick!r}"
                )
                return nickname

