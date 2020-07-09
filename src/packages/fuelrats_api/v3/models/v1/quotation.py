from __future__ import annotations

import typing
from datetime import datetime
from typing import Optional, Dict

import attr

from src.packages.fuelrats_api.v3.converters import to_datetime, from_datetime
from ..jsonapi.resource import Resource
from .....quotation import Quotation as InternalQuotation


@attr.dataclass
class QuotationAttributes:
    message: str = attr.ib(validator=attr.validators.instance_of(str))
    author: str = attr.ib(validator=attr.validators.instance_of(str))
    lastAuthor: str = attr.ib(validator=attr.validators.instance_of(str))
    createdAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=to_datetime
    )
    updatedAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=to_datetime
    )


@attr.dataclass
class Quotation(Resource):
    type: str = "quotations"
    attributes: Optional[QuotationAttributes] = None

    @classmethod
    def from_dict(cls, data: typing.Dict) -> Resource:
        return cls(id=data["id"], attributes=QuotationAttributes(**data["attributes"]))

    def to_dict(self) -> Dict:
        output = attr.asdict(self, recurse=True)
        output["attributes"]["createdAt"] = from_datetime(self.attributes.createdAt)
        output["attributes"]["updatedAt"] = from_datetime(self.attributes.updatedAt)
        return output

    def into_internal(self) -> InternalQuotation:
        return InternalQuotation(
            message=self.attributes.message,
            author=self.attributes.author,
            last_author=self.attributes.lastAuthor,
            created_at=self.attributes.createdAt,
            updated_at=self.attributes.updatedAt,
        )

    @classmethod
    def from_internal(cls, data: InternalQuotation) -> Quotation:
        return cls(
            attributes=QuotationAttributes(
                message=data.message,
                author=data.author,
                lastAuthor=data.last_author,
                createdAt=data.created_at,
                updatedAt=data.updated_at,
            ),
            id=None,
        )
