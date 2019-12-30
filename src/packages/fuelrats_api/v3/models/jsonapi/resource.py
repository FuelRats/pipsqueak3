from __future__ import annotations

import typing
from uuid import UUID

import attr

if typing.TYPE_CHECKING:
    from .relationship import Relationship
    from .link import Links


@attr.dataclass
class Resource:
    id: UUID
    type: typing.ClassVar[str]

    attributes: typing.Optional[typing.Dict] = None
    relationships: typing.Optional[typing.Dict[str, Relationship]] = None
    links: typing.Optional[Links] = attr.ib(
        default=None,
    )

    @classmethod
    def from_dict(cls, data: typing.Dict) -> Resource:
        return cls(**data)
