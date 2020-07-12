from __future__ import annotations

import abc
import typing
from typing import Optional, List
from uuid import UUID

import attr

if typing.TYPE_CHECKING:
    from ..rat.rat import Rat
    from ..rescue import Rescue
    from ._converter import ApiConverter


@attr.dataclass
class ApiConfig:
    online_mode: bool = attr.ib(validator=attr.validators.instance_of(bool))
    uri: str = attr.ib(validator=attr.validators.instance_of(str))
    authorization: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )


@attr.dataclass(eq=False)
class FuelratsApiABC(abc.ABC):
    rat_converter: ApiConverter[Rat]
    rescue_converter: ApiConverter[Rescue]
    config: ApiConfig
    __slots__ = ["rat_converter", "rescue_converter", "config"]

    @abc.abstractmethod
    async def get_rescues(self) -> typing.List[Rescue]:
        ...

    @abc.abstractmethod
    async def get_rescue(self, key: UUID) -> typing.Optional[Rescue]:
        ...

    @abc.abstractmethod
    async def create_rescue(self, rescue: Rescue) -> Rescue:
        ...

    @abc.abstractmethod
    async def update_rescue(self, rescue: Rescue) -> None:
        ...

    @abc.abstractmethod
    async def get_rat(self, key: typing.Union[UUID, str]) -> List[Rat]:
        ...


class ApiException(RuntimeError):
    ...
