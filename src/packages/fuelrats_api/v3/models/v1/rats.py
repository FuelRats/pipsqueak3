from __future__ import annotations

import typing
from datetime import datetime

import attr
from dateutil.parser import parse as parse_date

from ..jsonapi.relationship import Relationship
from ..jsonapi.resource import Resource
from .....rat import Rat as InternalRat
from .....utils import Platforms


def platform_converter(key: str):
    return Platforms[key.upper()]


@attr.dataclass
class RatRelationships:
    user: Relationship
    ships: Relationship

    @classmethod
    def from_dict(cls, data: typing.Dict):
        return cls(
            user=Relationship.from_dict(data["user"]), ships=Relationship.from_dict(data["ships"]),
        )


@attr.dataclass
class RatAttributes:
    name: str = attr.ib(validator=attr.validators.instance_of(str))
    createdAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=parse_date
    )
    updatedAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=parse_date
    )
    platform: Platforms = attr.ib(converter=platform_converter)
    frontierId: typing.Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    data: typing.Dict = attr.ib(factory=dict, validator=attr.validators.instance_of(dict))


@attr.dataclass
class Rat(Resource):
    attributes: RatAttributes = attr.ib(factory=RatAttributes)
    relationships: typing.Optional[RatRelationships] = None
    type: typing.ClassVar[str] = "rats"

    @classmethod
    def from_dict(cls, data: typing.Dict) -> Rat:
        attributes = RatAttributes(**data["attributes"])
        relationships = RatRelationships.from_dict(data["relationships"])
        return cls(attributes=attributes, relationships=relationships, id=data["id"])

    def as_internal_rat(self) -> InternalRat:
        """
        Converts this API rat to an Internal Rat object.
        """
        return InternalRat(uuid=self.id, name=self.attributes.name, platform=self.attributes.platform)
