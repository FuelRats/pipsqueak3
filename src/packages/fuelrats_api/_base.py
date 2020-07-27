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
Impersonation = typing.TypeVar("Impersonation", str, UUID)
""" Type for an ID of the user Mecha is performing an API action on the behalf of """

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
    async def get_rescues(self, impersonating: Impersonation) -> typing.List[Rescue]:
        """
        Retrieves open rescues

        Args:
            impersonating: the user this command is acting for

        Returns:
            List of internal rescue objects
        """
        ...

    @abc.abstractmethod
    async def get_rescue(self, key: UUID, impersonating: Impersonation) -> typing.Optional[Rescue]:
        """
        Gets a single rescue by its ID.

        Args:
            key: api uuid of rescue
            impersonating: the user this command is acting for

        Returns:
            InternalRescue, should it exist.
        """
        ...

    @abc.abstractmethod
    async def create_rescue(self, rescue: Rescue, impersonating: Impersonation) -> Rescue:
        """
        Creates a new rescue, returning the created InternalRescue object with any fields the
        API overrode.

        Notes:
            Use the return value of this function instead of the input argument in subsequent compute.

        Args:
            rescue: Internal Rescue to create on the API
            impersonating: User this action is on the behalf of.

        Returns:
            Internal Rescue object as formed by the API
        """
        ...

    @abc.abstractmethod
    async def update_rescue(self, rescue: Rescue, impersonating: Impersonation) -> None:
        ...

    @abc.abstractmethod
    async def get_rat(self, key: typing.Union[UUID, str], impersonating: Impersonation) -> List[Rat]:
        ...


class ApiException(RuntimeError):
    ...
