import asyncio
from typing import Dict, Coroutine

from websockets.client import WebSocketClientProtocol
from .protocol import Response, Request
from loguru import logger


class Connection:
    __slots__ = ["_socket", "_futures", "shutdown", "_work"]

    def __init__(self, socket):
        self._socket: WebSocketClientProtocol = socket
        self._futures: Dict[str, asyncio.Future] = {}
        self.shutdown = asyncio.Event()
        self._work: asyncio.Queue[Request] = asyncio.Queue()

        # spawn worker tasks
        asyncio.create_task(self.rx_worker())
        asyncio.create_task(self.tx_worker())

    async def rx_worker(self):
        """ worker that receives messages from the websocket """
        while not self.shutdown.is_set():
            # async block read from socket
            raw = await self._socket.recv()
            response = Response.deserialize(raw)
            logger.debug("parsed response:= {!r}", response)
            # check if we had a future for this, if so complete it.
            if response.state in self._futures:
                self._futures[response.state].set_result(response)
            else:
                logger.warning("got unsolicited response {!r}", response)

    async def tx_worker(self):
        """ Worker that sends messages to the websocket """
        while not self.shutdown.is_set():
            # async blocking get work
            work = await self._work.get()
            await self._socket.send(work.serialize())

    def execute(self, work: Request) -> asyncio.Future:

        # create a future, representing the Response that will satisfy this work item
        future = asyncio.Future()
        self._futures[work.state] = future
        # submit the item to the queue, for the tx_worker to pick up
        self._work.put_nowait(work)

        # return the future to the caller,who can then await the future
        return future
