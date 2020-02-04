import typing
from uuid import UUID

from .._base import FuelratsApiABC
from ...rat import Rat
from ...rescue import Rescue


class ApiV300(FuelratsApiABC):

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