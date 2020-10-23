import attr


@attr.dataclass
class CommandsConfigRoot:
    prefix: str = attr.ib(validator=attr.validators.instance_of(str), default="!")
    drill_mode: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
