from typing import Optional

import attr


@attr.dataclass
class FuelratsApiConfigRoot:
    online_mode: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
    uri: str = attr.ib(validator=attr.validators.instance_of(str), default="wss://localhost")
    authorization: Optional[str] = attr.ib(
        validator=attr.validators.optional(
            attr.validators.instance_of(str),
        ),
        default=None,
    )


@attr.dataclass
class StarsystemApiConfigRoot:
    url: str = attr.ib(
        validator=attr.validators.instance_of(str), default="https://system.api.fuelrats.com/"
    )
