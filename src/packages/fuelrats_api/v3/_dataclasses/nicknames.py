import typing
from datetime import datetime

import attr
import dateutil.parser

from src.packages.fuelrats_api.v3._dataclasses.jsonapi import Link
from src.packages.fuelrats_api.v3._dataclasses.jsonapi.link import Links
from .relationships import Relationship


@attr.dataclass
class NicknamesAttributes:
    lastQuit: str = attr.ib(validator=attr.validators.instance_of(str))
    lastRealHost: str = attr.ib(validator=attr.validators.instance_of(str))
    lastSeen: datetime = attr.ib(converter=dateutil.parser.parse)
    lastRealName: str = attr.ib(validator=attr.validators.instance_of(str))
    lastUserMask: str = attr.ib(validator=attr.validators.instance_of(str))
    display: str = attr.ib(validator=attr.validators.instance_of(str))
    nick: str = attr.ib(validator=attr.validators.instance_of(str))
    createdAt: datetime = attr.ib(converter=dateutil.parser.parse)
    updatedAt: typing.Optional[datetime] = attr.ib(
        converter=attr.converters.optional(dateutil.parser.parse)
    )
    vhost: typing.Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    email: str = attr.ib(validator=attr.validators.instance_of(str))
    score: int = attr.ib(validator=attr.validators.instance_of(int))
    """ edit distance from API match """


@attr.dataclass
class NicknamesRelationships:
    user: Relationship = attr.ib(validator=attr.validators.instance_of(Relationship))
    rat: Relationship = attr.ib(validator=attr.validators.instance_of(Relationship))


@attr.dataclass
class Nicknames:
    id: int
    attributes: NicknamesAttributes = attr.ib(
        validator=attr.validators.instance_of(NicknamesAttributes)
    )
    relationships: NicknamesRelationships = attr.ib(
        validator=attr.validators.instance_of(NicknamesRelationships)
    )
    links: Links = attr.ib(
        validator=attr.validators.deep_mapping(
            key_validator=attr.validators.instance_of(str),
            value_validator=attr.validators.instance_of(Link),
            mapping_validator=attr.validators.instance_of(dict),
        )
    )
    type: str = "nicknames"
