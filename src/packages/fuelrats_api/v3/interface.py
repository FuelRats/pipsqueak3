import asyncio
import typing
from typing import Optional, List
from uuid import UUID

import aiohttp
import attr
import websockets
from loguru import logger
from prometheus_client import Histogram

from .models.v1.nickname import Nickname
from .models.v1.rats import RatAttributes
from .websocket.client import Connection
from .websocket.protocol import Request, Response
from .._base import FuelratsApiABC, ApiConfig
from ...rat import Rat
from ...rescue import Rescue
from ....config import CONFIG_MARKER, PLUGIN_MANAGER

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

    def _call(self, query: str) -> asyncio.Future:
        ...

    async def find_nickname(self, key: str) -> Nickname:
        logger.trace("creating API session...")
        async with aiohttp.ClientSession(
                raise_for_status=True,
                timeout=aiohttp.ClientTimeout(total=5.0),
                headers={
                    "authorization": self.config.authorization} if self.config.authorization else {},
        ) as session:
            logger.trace(f"requesting nick={key!r}")
            async with session.request(
                    method="GET", url=f"{self.config.uri}/nicknames?nick={key}"
            ) as response:
                data = await response.json()
                logger.trace("got response, decoding")
                nickname = Nickname.from_dict(data["data"][0])
                logger.debug(
                    f"retrieved nickname object {nickname.id!r} - {nickname.attributes.nick!r}"
                )
                return nickname


@attr.dataclass(eq=False)
class ApiV300WSS(FuelratsApiABC):
    connection: Optional[Connection] = attr.ib(default=None)
    """ underlying websocket """

    def __attrs_post_init__(self):
        PLUGIN_MANAGER.register(self)

    @CONFIG_MARKER
    def rehash_handler(self, data: typing.Dict):
        """
        Apply new configuration data

        Args:
            data (typing.Dict): new configuration data to apply.

        """
        # grab original for comparison
        original = self.config
        new_configuration = ApiConfig(**data["api"])

        # apply new configuration
        self.config = new_configuration

        # If we don't have a connection (startup rehash) OR the configuration changed.
        if not self.connection or original != new_configuration:
            logger.info("New API configuration detected, applying changes...")
            # TODO: handle pending futures prior to shutdown
            if self.connection:
                self.connection.shutdown.set()

                # abandon the existing connection, it shut shut itself down as the shutdown event
                # is set.
                self.connection = None
            # only create a new connection
            if self.config.online_mode:
                # spawn new worker task
                asyncio.create_task(self.run_task())
        else:
            logger.info("API handler took no action on rehash, nothing to change!")

    @CONFIG_MARKER
    def validate_config(self, data: typing.Dict):  # pylint: disable=unused-argument
        """
        Validate new configuration data.

        Args:
            data (typing.Dict): new configuration data  to validate

        Raises:
            ValueError:  config section failed to validate.
            KeyError:  config section failed to validate.
        """
        relevant = data["api"]
        # attempt to construct api configuration; if this succeeds the config is acceptable.
        ApiConfig(**relevant)

    async def run_task(self):
        """
        create and run
        the
        websocket, spawn
        AS
        A
        TASK
        """
        logger.info("creating new socket connection....")
        async with websockets.connect(
                uri=f"{self.config.uri}?bearer={self.config.authorization}",
                subprotocols=('FR-JSONAPI-WS',)
        ) as soc:
            logger.info("created.")
            self.connection = Connection(socket=soc)
            logger.info("pending shutdown event...")
            await self.connection.shutdown.wait()

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

    async def _get_nicknames(self, key: str) -> Response:
        work = Request(endpoint=["nicknames", "search"], query={"nick": key}, )
        # TODO: offline check
        logger.info(f"querying nickname {key}")
        return await self.connection.execute(work)


    async def get_rats_from_nickname(self, key:str) -> List[Rat]:
        ...