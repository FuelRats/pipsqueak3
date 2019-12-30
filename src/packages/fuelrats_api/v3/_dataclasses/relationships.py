import typing

import attr

from src.packages.fuelrats_api.v3._dataclasses.jsonapi.link import Links


@attr.dataclass
class RelationshipData:
    type: str
    id: str


@attr.dataclass
class Relationship:
    links: typing.Optional[Links] = None
    data: typing.Optional[RelationshipData] = None
