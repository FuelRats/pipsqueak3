import typing

import attr


@attr.dataclass
class Link:
    href: str
    meta: typing.Dict = attr.ib(factory=dict)
