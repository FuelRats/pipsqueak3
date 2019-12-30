import typing

import attr

from src.packages.fuelrats_api.v3._dataclasses.jsonapi.resource import Resource


@attr.dataclass
class RelationshipMany(Resource):
    data: typing.Optional[typing.List[Resource]] = None
