import typing

from .. import ApiConverter
from .._converters.links_converter import LinksConverter
from .._dataclasses.relationships import Relationship, RelationshipData


class RelationshipConveter(ApiConverter[Relationship]):

    @classmethod
    def from_api(cls, data) -> typing.Dict[str, Relationship]:
        result = {}
        for key, obj in data.items():
            links = LinksConverter.from_api(obj['links'])
            data = obj['data']
            result[key] = Relationship(
                links=links,
                data=RelationshipData(**data) if data else None
            )

        return result
