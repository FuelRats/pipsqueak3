from __future__ import annotations

import typing
from abc import abstractmethod

from src.packages.rescue import Rescue

if typing.TYPE_CHECKING:
    from ..rat import Rat

_DTYPE = typing.TypeVar("_DTYPE")


class ApiConverter(typing.Protocol[_DTYPE]):
    @classmethod
    def to_api(cls, data: _DTYPE) -> typing.Dict:
        ...

    @classmethod
    @abstractmethod
    def from_api(cls, data: typing.Dict) -> _DTYPE:
        ...
