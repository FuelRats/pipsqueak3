from __future__ import annotations

from typing import Dict, Optional

import attr
from ..jsonapi.link import Links
from ...converters import to_uuid
from uuid import UUID, uuid4


@attr.dataclass
class Pointer:
    pointer: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)), default=None,
    )
    """
    If the error is a client error caused by an invalid entity in the request object a JSON pointer
    to it will be provided here.
    """
    parameter: str = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)), default=None,
    )
    """
    If the error is a client error caused by a query parameter the name of the query parameter will 
    be provided here.
    """

    @classmethod
    def from_dict(cls, data: Dict) -> Pointer:
        return cls(**data)


@attr.dataclass
class ApiError:
    id_: UUID = attr.ib(converter=to_uuid)
    links: Links = attr.ib(validator=attr.validators.instance_of(dict))
    status: str = attr.ib(validator=attr.validators.instance_of(str))
    code: int = attr.ib(validator=attr.validators.instance_of(int))
    title: str = attr.ib(validator=attr.validators.instance_of(str))
    detail: str = attr.ib(validator=attr.validators.instance_of(str))
    source: Pointer = attr.ib(validator=attr.validators.instance_of(Pointer))

    @classmethod
    def from_dict(cls, data: Dict) -> ApiError:
        data["id_"] = data["id"]
        del data["id"]
        data["source"] = Pointer.from_dict(data["source"])
        return cls(**data)


class APIException(Exception):
    def __init__(self, error: ApiError):
        self.error: ApiError = error
