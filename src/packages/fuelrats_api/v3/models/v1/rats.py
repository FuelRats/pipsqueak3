from __future__ import annotations

import typing
from datetime import datetime

import attr

from src.packages.fuelrats_api.v3.models.jsonapi.relationship import Relationship
from src.packages.utils import Platforms


def platform_converter(key: str):
    return Platforms[key.upper()]


@attr.dataclass
class RatRelationships:
    user: Relationship
    ships: Relationship
    epics: Relationship

    @classmethod
    def from_dict(cls, data: typing.Dict):
        return cls(
            user=Relationship.from_dict(data['user']),
            ships=Relationship.from_dict(data['ships']),
            epics=Relationship.from_dict(data['epics']),
        )


@attr.dataclass
class RatAttributes:
    createdAt: datetime
    updatedat: datetime
    platform: Platforms = attr.ib(converter=platform_converter)
    frontierId: typing.Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    data: typing.Dict = attr.ib(factory=dict, validator=attr.validators.instance_of(dict))
