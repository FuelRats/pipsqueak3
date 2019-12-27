from .links_converter import LinksConverter
from .relationship_converter import RelationshipConveter
from .. import ApiConverter
from .._dataclasses.nicknames import Nicknames, NicknamesAttributes, NicknamesRelationships


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
