from typing import List

import attr


@attr.dataclass
class RatmamaConfigRoot:
    announcer_nicks: List[str] = attr.ib(
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(str),
            iterable_validator=attr.validators.instance_of(list),
        ),
        default=["RatMama[Bot]"],
    )
    trigger_keyword: str = attr.attrib(
        validator=attr.validators.instance_of(str), default="TESTSIGNAL"
    )
