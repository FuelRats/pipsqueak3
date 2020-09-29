
import typing
from datetime import datetime

import attr

from src.packages.fuelrats_api.v3.converters import to_platform, to_datetime
from ..jsonapi.relationship import Relationship
from ..jsonapi.resource import Resource
from .....rat import Rat as InternalRat
from .....utils import Platforms

RAT_TYPE = "rats"


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
        validator=attr.validators.instance_of(datetime), converter=to_datetime
    )
    updatedAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=to_datetime
    )
    platform: Platforms = attr.ib(converter=to_platform)
    frontierId: typing.Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    data: typing.Dict = attr.ib(factory=dict, validator=attr.validators.instance_of(dict))


@attr.dataclass
class Rat(Resource):
    attributes: RatAttributes = attr.ib(factory=RatAttributes)
    relationships: typing.Optional[RatRelationships] = None
    type: str = RAT_TYPE

    @classmethod
    def from_dict(cls, data: typing.Dict) -> 'Rat':
        attributes = RatAttributes(**data["attributes"])
        relationships = RatRelationships.from_dict(data["relationships"])
        return cls(attributes=attributes, relationships=relationships, id=data["id"])

    def into_internal(self) -> InternalRat:
        """
        Converts this API rat to an Internal Rat object.
        """
        return InternalRat(uuid=self.id, name=self.attributes.name, platform=self.attributes.platform)
