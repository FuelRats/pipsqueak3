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
    createdAt: datetime = attr.ib(validator=attr.validators.instance_of(datetime))
    updatedAt: datetime = attr.ib(validator=attr.validators.instance_of(datetime))

    def into_internal(self) -> InternalQuotation:
        return InternalQuotation(
            message=self.message,
            author=self.author,
            last_author=self.lastAuthor,
            created_at=self.createdAt,
            updated_at=self.updatedAt,
        )

    @classmethod
    def from_internal(cls, data: InternalQuotation) -> "Quotation":
        return cls(
            message=data.message,
            author=data.author,
            lastAuthor=data.last_author,
            createdAt=data.created_at,
            updatedAt=data.updated_at,
        )
