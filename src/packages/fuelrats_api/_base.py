from __future__ import annotations

import abc
import typing
from uuid import UUID

import attr

if typing.TYPE_CHECKING:
    from ..rat.rat import Rat
    from ..rescue import Rescue
    from ._converter import ApiConverter


@attr.s
class FuelratsApiABC(abc.ABC):
    rat_converter: ApiConverter[Rat]
    rescue_converter: ApiConverter[Rescue]
    url: str = attr.ib(
        default="https://localhost:80/api", validator=attr.validators.instance_of(str)
    )

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
    async def get_rat(self, key: typing.Union[UUID, str]) -> Rat:
        ...
