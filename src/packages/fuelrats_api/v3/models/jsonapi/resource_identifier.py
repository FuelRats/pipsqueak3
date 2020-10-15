import typing
from uuid import UUID

import attr


@attr.dataclass
class ObjectIdentifier:
    type: str
    id: UUID
    meta: typing.Dict = attr.ib(factory=dict)
    """ optional non-standard data field """
