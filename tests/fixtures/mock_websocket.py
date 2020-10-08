from typing import List, Optional

import pytest

from src.packages.fuelrats_api._base import ApiConfig
from src.packages.fuelrats_api.v3.interface import ApiV300WSS, Connection
import attr
import asyncio

from src.packages.fuelrats_api.v3.websocket.protocol import Request, Response


@attr.dataclass
class Expectation:
    tx: Request
    rx: Response


class FakeConnection(Connection):
    """
    A Connection object that doesn't actually use a websocket.
    Instead it will run assertions against its `expectations` attribute,
    when something calls `execute(work)` on instances of this object, an assertion will
    be rendered against the expectations this connection was initialized with.
    When the assertion passes, the return value of the expectation is returned to the caller.

    Expectations are interpreted FIFO, and an exception will be raised if an unexpected message is
    received (execute() called when no execution was expected).
    """
    __slots__ = ["expectations"]

    def __init__(self, expectations: Optional[List[Expectation]] = None):
        self.expectations = expectations if expectations is not None else []
        super().__init__(socket=None, spawn_workers=False)

    def expect(self, request: Request, respond_with: Response):
        self.expectations.append(Expectation(tx=request, rx=respond_with))

    async def execute(self, work: Request) -> Response:
        assert self.expectations, "Request was not expected here."
        expectation = self.expectations.pop(0)
        work.state = expectation.rx.state
        assert expectation.tx == work, "work item was not expected here."
        return expectation.rx
