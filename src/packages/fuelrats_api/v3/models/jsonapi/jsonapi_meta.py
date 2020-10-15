import attr


@attr.dataclass
class JsonApiMeta:
    apiVersion: str = attr.ib(validator=attr.validators.instance_of(str))


@attr.dataclass
class JsonApi:
    version: str = attr.ib(validator=attr.validators.instance_of(str))
    meta: JsonApiMeta
