from __future__ import annotations

import typing
from datetime import datetime

import attr

from src.packages.fuelrats_api.v3.models.jsonapi.relationship import Relationship
from src.packages.fuelrats_api.v3.models.jsonapi.resource import Resource


@attr.dataclass
class NicknameRelationships:
    rat: Relationship
    user: Relationship

    @classmethod
    def from_dict(cls, data: typing.Dict):
        return cls(
            rat=Relationship.from_dict(data['rat']),
            user=Relationship.from_dict(data['user'])
        )


@attr.dataclass
class NicknameAttributes:
    lastQuit: typing.Optional[str] = None
    """The nickname's last IRC quit message.\nRead Permission: Public"""
    nick: str = ""
    """The nickname's last resolved hostname. \nRead Permission: Group"""
    lastRealHost: typing.Optional[str] = None
    """The nickname's last IRC real name.\nRead Permission: Public"""
    lastRealName: typing.Optional[str] = None
    """Timestamp for when the user was last seen on IRC\nRead Permission: Public"""
    lastSeen: typing.Optional[datetime] = None
    """The nickname's last known (hashed) usermask\nRead Permission: Public"""
    lastUserMask: typing.Optional[str] = None
    """The main nickname of the account this nickname belongs to\nRead Permission: Public"""
    display: typing.Optional[str] = None
    """The IRC nickname\nRead Permission: Public"""
    createdAt: typing.Optional[datetime] = None
    """Timestamp for when this nick was created\nRead Permission: Public"""
    updatedAt: typing.Optional[datetime] = None
    """Timestamp for when this nick was last updated\nRead Permission: Public"""
    vhost: typing.Optional[str] = None
    """The virtual-host of this nickname\nRead Permission: Public"""
    email: typing.Optional[str] = None
    "The email address this nickname belongs to Read Permission: Group"
    score: typing.Optional[int] = None
    """closeness to searched nickname"""


@attr.dataclass
class Nickname(Resource):
    """"""
    attributes: NicknameAttributes = attr.ib(factory=NicknameAttributes)
    relationships: typing.Optional[NicknameRelationships] = None
    type: typing.ClassVar[str] = "nicknames"

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            attributes=NicknameAttributes(**data['attributes']),
            relationships=NicknameRelationships.from_dict(data['relationships'])
        )
