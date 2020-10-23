import attr
from typing import List


@attr.dataclass
class IRCConfigRoot:
    nickname: str = attr.ib(validator=attr.validators.instance_of(str))
    server: str = attr.ib(validator=attr.validators.instance_of(str))
    port: int = attr.ib(validator=attr.validators.instance_of(int))
    tls: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
    channels: List[str] = attr.ib(
        factory=list,
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(str),
            iterable_validator=attr.validators.instance_of(list),
        ),
    )
