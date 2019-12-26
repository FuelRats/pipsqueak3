import typing

import attr


@attr.dataclass
class Links:
    href: str
    meta: typing.Dict = attr.ib(factory=dict)
