from __future__ import annotations

import typing
from datetime import datetime
from typing import Optional, Dict

import attr

from src.packages.fuelrats_api.v3.converters import to_datetime, from_datetime
from ..jsonapi.resource import Resource
from .....quotation import Quotation as InternalQuotation


@attr.dataclass
class Quotation:
    message: str = attr.ib(validator=attr.validators.instance_of(str))
    author: str = attr.ib(validator=attr.validators.instance_of(str))
    lastAuthor: str = attr.ib(validator=attr.validators.instance_of(str))
    createdAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=to_datetime
    )
    updatedAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=to_datetime
    )

    @classmethod
    def from_dict(cls, data: typing.Dict) -> Quotation:
        return cls(**data)

    def to_dict(self) -> Dict:
        output = attr.asdict(self, recurse=True)
        output["createdAt"] = from_datetime(self.attributes.createdAt)
        output["updatedAt"] = from_datetime(self.attributes.updatedAt)
        return output

    def into_internal(self) -> InternalQuotation:
        return InternalQuotation(
            message=self.message,
            author=self.author,
            last_author=self.lastAuthor,
            created_at=self.createdAt,
            updated_at=self.updatedAt,
        )

    @classmethod
    def from_internal(cls, data: InternalQuotation) -> Quotation:
        return cls(
            message=data.message,
            author=data.author,
            lastAuthor=data.last_author,
            createdAt=data.created_at,
            updatedAt=data.updated_at,
        )
