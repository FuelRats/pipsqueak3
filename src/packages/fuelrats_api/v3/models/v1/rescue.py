from __future__ import annotations

import typing
from typing import Optional, Dict, List, Any

import attr

from ..jsonapi.relationship import Relationship
from ..jsonapi.resource import Resource
from .....rescue import Rescue as InternalRescue
from datetime import datetime
from .converters import to_platform
from .converters import to_datetime
@attr.dataclass
class RescueAttributes:
    client: str = attr.ib(validator=attr.validators.instance_of(str))
    clientNick: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    clientLanguage: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    codeRed: bool = attr.ib(validator=attr.validators.instance_of(bool))
    data: Dict = attr.ib(validator=attr.validators.instance_of(dict))  # ???
    notes: str = attr.ib(validator=attr.validators.instance_of(str))
    platform: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    system: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    title: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    unidentifiedRats: List[str] = attr.ib(
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(str),
            iterable_validator=attr.validators.instance_of(list)
        )
    )
    createdAt: datetime = attr.ib(validator=attr.validators.instance_of(datetime), converter=to_datetime)
    updatedAt: datetime = attr.ib(validator=attr.validators.instance_of(datetime), converter=to_datetime)
    status: str = attr.ib(validator=attr.validators.instance_of(str))
    outcome: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    quotes: List = attr.ib()
    commandIdentifier:Any = attr.ib()


@attr.dataclass
class RescueRelationships:
    rats: Relationship
    firstLimpet: Relationship
    epics: Relationship


@attr.dataclass
class Rescue(Resource):
    type = "rescues"
    attributes: Optional[RescueAttributes] = None
    relationships: Optional[RescueRelationships] = None

    @classmethod
    def from_dict(cls, data: typing.Dict) -> Rescue:
        relationships = RescueRelationships(
            rats=Relationship.from_dict(data['relationships']['rats']),
            firstLimpet=Relationship.from_dict(data['relationships']['firstLimpet']),
            epics=Relationship.from_dict(data['relationships']['epics'])
        )
        return cls(
            id=data['id'],
            relationships=relationships,
            attributes=RescueAttributes(**data['attributes'])
        )

    def as_internal(self) -> InternalRescue:
        return InternalRescue(
            uuid = self.id,
            client=self.attributes.client,
            system=self.attributes.system,
            irc_nickname=self.attributes.clientNick,
            created_at=self.attributes.createdAt,
            updated_at=self.attributes.updatedAt,
            unidentified_rats=self.attributes.unidentifiedRats,
            quotes=self.attributes.quotes
            # TODO rest of attributes
        )