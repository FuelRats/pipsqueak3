from typing import Optional

import attr


@attr.dataclass(frozen=True)
class GelfConfig:
    enabled: bool = attr.ib(validator=attr.validators.instance_of(bool))
    port: Optional[int] = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(int)))
    host: Optional[str] = attr.ib(validator=attr.validators.optional(attr.validators.instance_of(str)))

    log_level: str = attr.ib(default="DEBUG", validator=attr.validators.instance_of(str))
    send_context: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)


@attr.dataclass
class LoggingConfigRoot:
    gelf: GelfConfig = attr.ib(validator=attr.validators.instance_of(GelfConfig))
    base_logger: str = attr.ib(validator=attr.validators.instance_of(str))
    log_file: str = attr.ib(validator=attr.validators.instance_of(str))
