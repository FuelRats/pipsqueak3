from __future__ import annotations

import typing
from typing import Optional, Dict, List, Set

import attr

from ..jsonapi.relationship import Relationship
from ..jsonapi.resource import Resource
from .....rescue import Rescue as InternalRescue
from .....mark_for_deletion import MarkForDeletion
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
        data["quotes"] = [Quotation.from_dict(obj) for obj in data["quotes"]]
        return cls(**data)

    @classmethod
    def from_internal(cls, data: InternalRescue) -> RescueAttributes:

        return cls(
            client=data.client,
            clientNick=data.irc_nickname,
            clientLanguage=data.lang_id,
            codeRed=data.code_red,
            data={},
            # MFD reason translates into the notes field
            notes=data.marked_for_deletion.reason if data.marked_for_deletion.marked else "",
            platform=data.platform.value.lower() if data.platform else None,
            system=data.system,
            title=data.title,
            unidentifiedRats=[obj.name for obj in data.unidentified_rats.values()],
            createdAt=data.created_at,
            updatedAt=data.updated_at,
            status=data.status.name.lower(),
            # MFD translates to `purge` outcome, all other outcomes are not set by Mecha.
            outcome="purge" if data.marked_for_deletion.marked else None,
            quotes=[Quotation.from_internal(obj) for obj in data.quotes],
            # I did have to ask what this translated to...
            commandIdentifier=data.board_index,

        )


@attr.dataclass
class RescueRelationships:
    rats: Relationship
    firstLimpet: Relationship
    epics: Relationship


@attr.dataclass
class Rescue(Resource):
    type: str = "rescues"
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
            attributes=RescueAttributes.from_dict(data["attributes"]),
        )

    def into_internal(self) -> InternalRescue:
        return InternalRescue(
            uuid=self.id,
            client=self.attributes.client,
            system=self.attributes.system,
            irc_nickname=self.attributes.clientNick,
            created_at=self.attributes.createdAt,
            updated_at=self.attributes.updatedAt,
            unidentified_rats=self.attributes.unidentifiedRats,
            quotes=[quote.into_internal() for quote in self.attributes.quotes],
            title=self.attributes.title,
            first_limpet=self.relationships.firstLimpet.data.id
            if self.relationships and self.relationships.firstLimpet.data
            else None,
            board_index=self.attributes.commandIdentifier,
            lang_id=self.attributes.clientLanguage,
            # TODO rest of attributes
            mark_for_deletion=MarkForDeletion(
                marked=self.attributes.outcome == "purge",
                reason=self.attributes.notes if self.attributes.notes else None
            )
        )

    @classmethod
    def from_internal(cls, data: InternalRescue) -> Rescue:
        return Rescue(id=data.api_id, attributes=RescueAttributes.from_internal(data))

    def to_delta(self, changes: Set[str]) -> Dict:
        """
        Converts this API rescue object to a dictionary blob delta based on changed fields from
        an internal rescue object. `changes` should contain only attribute names on the **internal**
        rescue object.



        Args:
            changes: set of changed InternalRescue attributes

        Returns:
            json blob of API Rescue
        """
        field_map = {
            "client": "client",
            "system": "system",
            "irc_nick": "clientNick",
            "unidentified_rats": "unidentifiedRats",
            "quotes": "quotes",
            "title": "title",
            "board_index": "commandIdentifier",
            "lang_id": "clientLanguage",
            "status": "status",
            "code_red": "codeRed",
            "platform": "platform",
        }
        # translate internal datamodel names to the APIs datamodel names
        keep = {field_map[field] for field in changes if field != 'mark_for_deletion'}
        # serialize API rescue object
        data = attr.asdict(self, recurse=True)
        # figure out which keys we need to keep (only send the ones modified internally)
        kept_attribs = {key: value for key, value in data["attributes"].items() if key in keep}
        # and patch the object.
        data["attributes"] = kept_attribs
        return data
