import attr


@attr.dataclass
class BoardConfigRoot:
    cycle_at: int = attr.ib(validator=attr.validators.instance_of(int))
