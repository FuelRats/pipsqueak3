import asyncio
import typing
from typing import Optional, List, Dict, Union, Iterator
from uuid import UUID

import aiohttp
import attr
import cattr
import websockets
from loguru import logger
from prometheus_client import Histogram

from .models.v1.nickname import Nickname
from .models.v1.rats import Rat as ApiRat, RAT_TYPE
from .models.v1.rescue import Rescue as ApiRescue
from .models.jsonapi.resource import Resource
from .websocket.client import Connection, Hardfail
from .websocket.protocol import Request, Response
from .._base import FuelratsApiABC, Impersonation
from ...rat import Rat as InternalRat
from ...rescue import Rescue
from ....config import CONFIG_MARKER, PLUGIN_MANAGER
from .models.v1.apierror import UnauthorizedImpersonation, APIException
from ....config.datamodel import ConfigRoot

NICKNAME_TIME = Histogram(
    namespace="api",
    name="fetching_nicknames",
    unit="seconds",
    documentation="time spent retrieving nicknames...",
)


@attr.dataclass(eq=False)
class ApiV300WSS(FuelratsApiABC):
    connection: Optional[Connection] = attr.ib(default=None)
    """ underlying websocket """
    connected_event: asyncio.Event = attr.ib(factory=asyncio.Event)

    def __attrs_post_init__(self):
        PLUGIN_MANAGER.register(self)
        if self.connection is None:
            asyncio.create_task(self.run_task())

    @CONFIG_MARKER
    def rehash_handler(self, data: ConfigRoot):
        """
        Apply new configuration data

        Args:
            data (Dict): new configuration data to apply.

        """
        # grab original for comparison
        original = self.config
        new_configuration = data.api

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

    async def run_task(self):
        """
        create and run
        the
        websocket, spawn
        AS
        A
        TASK
        """
        # Ensure we have a new event signal.
        self.connected_event = asyncio.Event()
        logger.info("creating new socket connection....")
        async with websockets.connect(
            uri=f"{self.config.uri}?bearer={self.config.authorization}",
            subprotocols=("FR-JSONAPI-WS",),
        ) as soc:
            logger.info("created.")
            self.connection = Connection(socket=soc)
            self.connected_event.set()
            logger.info("pending shutdown event...")
            await self.connection.shutdown.wait()

    async def get_rescues(self, impersonate: Impersonation) -> List[Rescue]:
        return [obj.into_internal() for obj in await self._get_open_rescues(impersonate=impersonate)]

    async def update_rescue(self, rescue: Rescue, impersonating: Impersonation) -> None:
        await self.ensure_connection()
        if not rescue.api_id:
            raise ValueError("Rescue cannot have a null API ID at this point.")
        payload = {
            "data": ApiRescue.from_internal(rescue).to_delta(rescue.modified.copy()),
        }
        # Purge attributes we are not supposed to send.
        del payload["data"]["links"]
        del payload["data"]["relationships"]
        work = Request(
            endpoint=["rescues", "update"],
            body=payload,
            query={"id": f"{rescue.api_id}", "representing": impersonating},
        )
        if not Impersonation:
            del work.query["representing"]
        response = await self.execute(work)
        return response

    async def _get_rescue(self, key: UUID, impersonation: Impersonation) -> Optional[ApiRescue]:
        await self.ensure_connection()
        work = Request(
            endpoint=["rescues", "read"], query={"id": f"{key}", "representing": impersonation}
        )
        response = await self.execute(work)
        return cattr.structure(response.body["data"], Optional[ApiRescue])

    async def get_rescue(self, key: UUID, impersonation: Impersonation) -> typing.Optional[Rescue]:
        rescue = await self._get_rescue(key=key, impersonation=impersonation)
        if rescue:
            return rescue.into_internal()

    async def ensure_connection(self):
        if not self.connected_event.is_set():
            logger.trace("waiting for the connected event to be set...")
            # wait for a short period for the connection to be established, but not indefinitely.
            await asyncio.wait_for(fut=await self.connected_event.wait(), timeout=5)

        logger.trace("connected event is set!")

    async def create_rescue(self, rescue: Rescue, impersonating: Impersonation) -> Rescue:
        await self.ensure_connection()
        work = Request(
            endpoint=["rescues", "create"],
            query={"representing": impersonating},
            body={"data": attr.asdict(ApiRescue.from_internal(rescue), recurse=True)},
        )
        result = await self.execute(work)
        # if we get this far, we got a OK response; which means the data field contains our rescue.
        payload: ApiRescue = cattr.structure(result.body["data"], ApiRescue)
        return payload.into_internal()

    async def get_rat(self, key: Union[UUID, str], impersonation: Impersonation) -> List[InternalRat]:
        await self.ensure_connection()
        if isinstance(key, UUID):
            results = await self._get_rat_uuid(key, impersonation=None)
            rat: ApiRat = cattr.structure(results.body["data"], ApiRat)
            return [rat.into_internal()]
        if isinstance(key, str):
            results = await self._get_rats_from_nickname(key, impersonation=impersonation)
            return [rat.into_internal() for rat in results]
        raise TypeError(type(key))

    async def _get_nicknames(self, key: str, impersonation: Impersonation) -> Response:
        await self.ensure_connection()

        work = Request(
            endpoint=["nicknames", "search"],
            query={"nick": key, "representing": impersonation},
        )
        # TODO: offline check
        logger.info(f"querying nickname {key}")
        return await self.execute(work)

    async def _get_rat_uuid(self, key: UUID, impersonation: Impersonation):
        await self.ensure_connection()

        work = Request(
            endpoint=["rats", "read"], query={"id": f"{key}", "representing": impersonation}
        )
        logger.debug("requesting rat {}", work)
        return await self.execute(work)

    async def _get_open_rescues(self, impersonate: Impersonation) -> List[ApiRescue]:
        await self.ensure_connection()
        work = Request(
            endpoint=["rescues", "search"], query={"filter": {"status": {"eq": "open"}}}, body={}
        )
        logger.trace("requesting open rescues...")
        results = await self.execute(work)
        # Iterators are less expensive than comprehensions (differed compute).
        structured_data = cattr.structure(results.body["data"], List[ApiRescue])
        return structured_data

    async def _get_rats_from_nickname(self, key: str, impersonation: Impersonation) -> List[ApiRat]:
        await self.ensure_connection()

        raw = await self._get_nicknames(key, impersonation=impersonation)
        # If comparing types by equality triggers you, you arn't alone.
        # Its not actually a type, but a string the API uses to represent one.
        # meaning the below is just a string equality operation; nothing untoward here.
        rats = [
            cattr.structure(obj, ApiRat) for obj in raw.body["included"] if obj["type"] == RAT_TYPE
        ]
        logger.debug("filtered Rats from nickname result: {!r}", rats)

        return rats

    async def execute(self, work: Request, retry: bool = False) -> Response:
        """
        Attempts to execute the work item against the underlying connection.

        This method will attempt to retry if a retry has not been attempted (`retry`=False).
            This method achieves that by destroying the existing connection and restarting the
            Relevant worker, then recursively calling itself with retry=True

        Args:
            work: work item
            retry: is this call a retry attempt?

        Returns:
            Response object

        Raises:
            Hardfail from underlying API error, if connection is still dead after a retry.
        """
        await self.ensure_connection()

        try:
            # attempt to invoke the underlying connection work item
            return await self.connection.execute(work=work)
        # If this fails hard, spark needs to attempt to reconnect (unless its already tried.)
        except Hardfail:
            # unconditionally kill the connection.
            self.connection.shutdown.set()
            if not retry:
                logger.exception("API hard failure detected, attempting to recover...")
                # kill the old connection, since its in a hardfail state
                self.connection.shutdown.set()
                # re-create the run_task, which creates a new connection.
                asyncio.create_task(self.run_task())
                # recursively call this routine, as its possible to fail more than once.
                return await self.execute(work=work, retry=True)
            raise
