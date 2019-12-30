from __future__ import annotations

import typing

import attr
from loguru import logger

from .link import ResourceLinkage, Links, Link
from .resource_identifier import ObjectIdentifier


@attr.dataclass
class Relationship:
    data: ResourceLinkage = None
    links: Links = attr.ib(factory=dict)
    meta: typing.Dict = attr.ib(factory=dict)

    @classmethod
    def from_dict(cls, payload) -> Relationship:
        # FIXME handle alternate form if data is present
        logger.debug("creating Relationship from {}", payload)
        kwargs = {}

        # check if we have a links object
        if "links" in payload:
            kwargs['links'] = {key: Link.from_dict(value) for key, value in payload['links'].items()}

        data = payload['data']
        if isinstance(data, list):
            # list of identifiers
            kwargs['data'] = [ObjectIdentifier(**item) for item in data]
        elif isinstance(data, dict):
            # single identifier
            kwargs['data'] = ObjectIdentifier(**data)
        elif data is None:
            # null is permissible here
            kwargs['data'] = None

        kwargs['meta'] = payload.get('meta', {})
        return cls(
            **kwargs
        )
