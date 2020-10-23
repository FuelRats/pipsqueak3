from typing import List, Set

import attr


@attr.dataclass
class RatmamaConfigRoot:
    announcer_nicks: Set[str] = attr.ib(
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(str),
            iterable_validator=attr.validators.instance_of(set),
        ),
        default=["RatMama[Bot]"],
    )
    trigger_keyword: str = attr.attrib(
        validator=attr.validators.instance_of(str), default="TESTSIGNAL"
    )

    def __attrs_post_init__(self):
        # Casefold nicks after instantiation
        # as its not worth adding a custom decode hook to do this in cattrs.
        self.announcer_nicks = {nick.casefold() for nick in self.announcer_nicks}
        # Assert we didn't somehow invalidate the dataclass.
        attr.validate(self)
