import typing
from typing import Optional

import attr
import pendulum

from ..jsonapi.relationship import Relationship
from ..jsonapi.resource import Resource
from .....rat import Rat as InternalRat
from .....utils import Platforms

RAT_TYPE = "rats"


@attr.dataclass
class RatRelationships:
    user: Relationship
    ships: Optional[Relationship] = attr.ib(default=None)

    @classmethod
    def from_dict(cls, data: typing.Dict):
        return cls(
            user=Relationship.from_dict(data["user"]),
            ships=Relationship.from_dict(data["ships"]),
        )


@attr.dataclass
class RatAttributes:
    name: str = attr.ib(validator=attr.validators.instance_of(str))
    createdAt: pendulum.DateTime = attr.ib(
        validator=attr.validators.instance_of(pendulum.DateTime),
    )
    updatedAt: pendulum.DateTime = attr.ib(
        validator=attr.validators.instance_of(pendulum.DateTime),
    )
    platform: Platforms = attr.ib()
    frontierId: typing.Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    data: typing.Dict = attr.ib(factory=dict, validator=attr.validators.instance_of(dict))


@attr.dataclass
class Rat(Resource):
    attributes: RatAttributes = attr.ib(factory=RatAttributes)
    relationships: typing.Optional[RatRelationships] = None
    type: str = RAT_TYPE

    def into_internal(self) -> InternalRat:
        """
        Converts this API rat to an Internal Rat object.
        """
        return InternalRat(uuid=self.id, name=self.attributes.name, platform=self.attributes.platform)
