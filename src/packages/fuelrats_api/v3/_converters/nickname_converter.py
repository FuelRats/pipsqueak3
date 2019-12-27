from .links_converter import LinksConverter
from .. import ApiConverter
from .._dataclasses.nicknames import Nicknames, NicknamesAttributes, NicknamesRelationships
from .._dataclasses.relationships import RelationshipData, Relationship


class RelationshipConveter(ApiConverter[Relationship]):

    @classmethod
    def from_api(cls, data):
        result = {}
        for key, obj in data.items():
            links = LinksConverter.from_api(obj['links'])
            data = obj['data']
            result[key] = Relationship(
                links=links,
                data=RelationshipData(**data) if data else None
            )

        return result


class NicknameConverter(ApiConverter[Nicknames]):
    @classmethod
    def from_api(cls, data):
        _type = data['type']
        _id = data['id']
        relationships = RelationshipConveter.from_api(data['relationships'])
        attributes = NicknamesAttributes(**data['attributes'])

        links = LinksConverter.from_api(data['links'])
        return Nicknames(
            id=_id,
            type=_type,
            relationships=NicknamesRelationships(**relationships),
            attributes=attributes,
            links=links
        )
