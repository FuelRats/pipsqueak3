from __future__ import annotations

import typing
from typing import Optional, Dict, List

import attr

from ..jsonapi.relationship import Relationship
from ..jsonapi.resource import Resource
from .....rescue import Rescue as InternalRescue
from datetime import datetime
from src.packages.fuelrats_api.v3.converters import to_datetime
from .quotation import Quotation


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
            iterable_validator=attr.validators.instance_of(list),
        )
    )
    createdAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=to_datetime
    )
    updatedAt: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime), converter=to_datetime
    )
    status: str = attr.ib(validator=attr.validators.instance_of(str))
    outcome: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    quotes: List[Quotation] = attr.ib(
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(Quotation),
            iterable_validator=attr.validators.instance_of(list),
        )
    )
    commandIdentifier: Optional[int] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)),
        converter=attr.converters.optional(int),
    )
    """ Board index. """

    @classmethod
    def from_dict(cls, data: Dict) -> RescueAttributes:
        data = data.copy()  # shallow copy because callers might get confused if we mutate theirs...
        data['quotes'] = [Quotation.from_dict(obj) for obj in data['quotes']]
        return cls(**data)

    @classmethod
    def from_internal(cls, data: InternalRescue) -> RescueAttributes:
        return cls(
            client=data.client,
            clientNick=data.irc_nickname,
            clientLanguage=data.lang_id,
            codeRed=data.code_red,
            data={},
            notes="",  # FIXME add notes to internal data model or?
            platform=data.platform.value.lower() if data.platform else None,
            system=data.system,
            title=data.title,
            unidentifiedRats=[obj.name for obj in data.unidentified_rats.values()],
            createdAt=data.created_at,
            updatedAt=data.updated_at,
            status=data.status.name.lower(),
            outcome=data.outcome,
            quotes=[Quotation.from_internal(obj) for obj in data.quotes],
            commandIdentifier=data.board_index
        )


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
            rats=Relationship.from_dict(data["relationships"]["rats"]),
            firstLimpet=Relationship.from_dict(data["relationships"]["firstLimpet"]),
            epics=Relationship.from_dict(data["relationships"]["epics"]),
        )
        return cls(
            id=data["id"],
            relationships=relationships,
            attributes=RescueAttributes.from_dict(data['attributes']),
        )

    def as_internal(self) -> InternalRescue:
        return InternalRescue(
            uuid=self.id,
            client=self.attributes.client,
            system=self.attributes.system,
            irc_nickname=self.attributes.clientNick,
            created_at=self.attributes.createdAt,
            updated_at=self.attributes.updatedAt,
            unidentified_rats=self.attributes.unidentifiedRats,
            quotes=[quote.as_internal() for quote in self.attributes.quotes],
            title=self.attributes.title,
            first_limpet=self.relationships.firstLimpet.data.id
            if self.relationships.firstLimpet.data
            else None,
            board_index=self.attributes.commandIdentifier,
            lang_id=self.attributes.clientLanguage,

            # TODO rest of attributes
        )

    @classmethod
    def from_internal(cls, data: InternalRescue) -> Rescue:
        return Rescue(
            id=data.api_id,
            attributes=RescueAttributes.from_internal(data)
        )
