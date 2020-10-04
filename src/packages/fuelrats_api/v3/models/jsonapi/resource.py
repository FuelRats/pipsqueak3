import typing
from typing import Optional
from uuid import UUID

import attr

from .relationship import Relationship
from .link import Links
from ...converters import to_uuid


@attr.dataclass
class Resource:
    id: Optional[UUID] = attr.ib(converter=attr.converters.optional(to_uuid))
    type: str = "Resource"

    attributes: typing.Optional[typing.Dict] = None
    relationships: typing.Optional[typing.Dict[str, Relationship]] = None
    links: typing.Optional[Links] = attr.ib(default=None, )
