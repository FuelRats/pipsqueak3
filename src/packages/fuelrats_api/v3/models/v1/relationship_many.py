import typing

import attr

from src.packages.fuelrats_api.v3.models.jsonapi.resource import Resource


@attr.dataclass
class RelationshipMany(Resource):
    data: typing.Optional[typing.List[Resource]] = None
