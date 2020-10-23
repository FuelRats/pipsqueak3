import attr


@attr.dataclass
class DatabaseConfigRoot:
    host: str = attr.ib(validator=attr.validators.instance_of(str))
    port: int = attr.ib(validator=attr.validators.instance_of(int))
    dbname: str = attr.ib(validator=attr.validators.instance_of(str))
    username: str = attr.ib(validator=attr.validators.instance_of(str))
    password: str = attr.ib(validator=attr.validators.instance_of(str))
    fact_table: str = attr.ib(validator=attr.validators.instance_of(str), default="fact")
    fact_log: str = attr.ib(validator=attr.validators.instance_of(str), default="fact_log")
