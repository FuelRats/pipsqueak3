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
        """
        TODO: flesh this out... probably need some form of conditionals to be useful...

        Returns: List of :class:`Rescue` objects
        """
        ...

    @abc.abstractmethod
    async def get_rescue(self, key: UUID) -> typing.Optional[Rescue]:
        """ Fetches a specific rescue from the API by its UUID, should it exist """
        ...

    @abc.abstractmethod
    async def create_rescue(self, rescue: Rescue) -> Rescue:
        """
        Creates a new rescue on the API based on the passed rescue

        Args:
            rescue: Rescue to create on the API

        Returns:
            :class:`Rescue` created Rescue object

        Notes:
            the returned rescue may be different than the passed, as the API fills some data in that we
            are not responisble for (IE the api_id)
        """
        ...

    @abc.abstractmethod
    async def update_rescue(self, rescue: Rescue) -> None:
        """ Updates an existing rescue on the API against local data """
        ...

    @abc.abstractmethod
    async def get_rat(self, key: typing.Union[UUID, str]) -> Rat:
        """ Fetches a :class:`Rat` from the API by its ID or nickname """
        ...
