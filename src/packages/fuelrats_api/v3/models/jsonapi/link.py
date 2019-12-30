import typing

import attr

from .resource_identifier import ObjectIdentifier


@attr.dataclass
class Link:
    href: str
    meta: typing.Dict = attr.ib(factory=dict)

    @classmethod
    def from_dict(cls, payload):
        # https://jsonapi.org/format/#document-links
        if isinstance(payload, str):
            # links type A
            return cls(href=payload)
        # links type B
        return cls(**payload)


Links = typing.Dict[str, Link]

ResourceLinkage = typing.Union[typing.List[ObjectIdentifier], ObjectIdentifier, None]
