import asyncio
import json
from typing import Dict, Union

import cattr
from loguru import logger
from src.packages.utils.ratlib import try_parse_uuid
from websockets.client import WebSocketClientProtocol

from .protocol import Response, Request
from .events import RescueUpdate, CLS_FOR_EVENT
from .. import event_converter
from ..models.v1.apierror import APIException, ApiError, UnauthorizedImpersonation


class Connection:
    __slots__ = ["_socket", "_futures", "shutdown", "_work", "_rx_worker", "_tx_worker",
                 "_fail_worker"]

    def __init__(self, socket):
        self._socket: WebSocketClientProtocol = socket
        self._futures: Dict[str, asyncio.Future] = {}
        self.shutdown = asyncio.Event()
        self._work: asyncio.Queue[Request] = asyncio.Queue()

        # spawn worker tasks
        self._rx_worker = asyncio.create_task(self.rx_worker())
        self._tx_worker = asyncio.create_task(self.tx_worker())
        self._fail_worker = asyncio.create_task(self.fail_watchdog())

    async def _handle_response(self, response: Response):
        logger.debug("parsed response:= {!r}", response)
        # check if we had a future for this, if so complete it.
        if response.state in self._futures:
            # if its an error return, then set the exception so the consumer raises.
            if response.status < 200 or response.status >= 300:
                the_error = ApiError.from_dict(response.body["errors"][0])
                if the_error.code == 401 and the_error.source.parameter == 'representing':
                    return self._futures[response.state].set_exception(
                        UnauthorizedImpersonation(the_error))
                return self._futures[response.state].set_exception(APIException(the_error))

            self._futures[response.state].set_result(response)
            # Watchers have their own handle to this, and we are done with it.
            # Drop handle from active monitoring.
            del self._futures[response.state]
        else:
            if response.status != 200:
                raise APIException(ApiError.from_dict(response.body["errors"][0]))
            logger.warning("got unsolicited response {!r}", response)

    async def _handle_event(self, event: RescueUpdate):
        logger.debug("recv'ed API event {!r}", event)

    async def rx_worker(self):
        """ worker that receives messages from the websocket """
        while not self.shutdown.is_set():
            # async block read from socket
            raw = await self._socket.recv()
            raw_data = json.loads(raw)
            if try_parse_uuid(raw_data[0]):
                response = Response(*raw_data)
                with logger.contextualize(state=response.state):
                    await self._handle_response(response)
                continue
            else:
                event = event_converter.structure(raw_data, CLS_FOR_EVENT[raw_data[0]])
                with logger.contextualize(event=raw_data[0]):
                    await self._handle_event(event)
                continue

    async def fail_watchdog(self):
        """
        Watchdog task that periodically checks that the other workers haven't died.

        If they have, mark any in-flight futures as failed with exception,
        as we are in an invalid state.
        """
        while not self.shutdown.is_set():
            fail = None

            await asyncio.sleep(1)
            logger.trace("watchdog tick.")

            if self._tx_worker.done():
                fail = self._tx_worker.exception()
            if self._rx_worker.done():
                fail = self._rx_worker.exception()
            if fail:
                logger.exception("TX/RX hardfail {}", fail)
                # We are in an invalid state, signal we died.
                self.shutdown.set()

                # Propagate failure to any in-flight futures, as they cannot possibly succeed now.
                for task in self._futures.values():
                    # Its possible to have done tasks in here (race)
                    # and setting the exception of a done task is a runtime error.
                    if not task.done():
                        task.set_exception(fail)

    async def tx_worker(self):
        """ Worker that sends messages to the websocket """
        while not self.shutdown.is_set():
            # async blocking get work
            work = await self._work.get()
            with logger.contextualize(state=work.state):
                if 'representing' in work.query:
                    # FIXME remove this hack once the API actually has production data...
                    # TODO: check drill mode and selectively not emit?
                    del work.query['representing']
                await self._socket.send(work.serialize())

    async def execute(self, work: Request) -> Response:
        await self.check_fail()

        # create a future, representing the Response that will satisfy this work item
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self._futures[work.state] = future
        # submit the item to the queue, for the tx_worker to pick up
        self._work.put_nowait(work)

        await self.check_fail()
        # await the future to complete in another task.
        result = await future

        await self.check_fail()

        return result

    async def check_fail(self):
        # check if either of our workers exploded on us
        # we do this here since exceptions cannot otherwise be meaningfully handled,
        # as the caller of this method is probably not doing so from a unmonitored task
        if self._rx_worker.done() and self._rx_worker.exception():
            raise self._rx_worker.exception()
        if self._tx_worker.done() and self._tx_worker.exception():
            raise self._tx_worker.exception()
        if self._fail_worker.done() and self._fail_worker.exception():
            raise self._fail_worker.exception()
