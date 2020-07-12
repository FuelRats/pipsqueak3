from typing import List

import attr
import asyncio


@attr.dataclass
class Expectation:
    tx: str
    rx: str


@attr.dataclass
class FakeWebsocket:
    expectations: List[Expectation]
    rx_future: asyncio.Future[str] = attr.ib(factory=asyncio.Future, init=False)

    async def recv(self) -> str:
        assert self.expectations, "wasn't expecting to reply."
        return await asyncio.wait_for(self.rx_future, 10.0)

    async def send(self, data: str) -> None:
        assert self.expectations, "wasn't expecting to transmit"
        expected = self.expectations.pop(0)  # treat as FIFO
        assert data == expected.tx, "Unexpected TX."
        self.rx_future.set_result(expected.rx)

    def expect(self, tx: str, rx: str) -> None:
        self.expectations.append(Expectation(tx=tx, rx=rx))
