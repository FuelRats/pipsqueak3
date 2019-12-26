from .. import ApiConverter
from .._dataclasses.nicknames import Nicknames, NicknamesRelationships, NicknamesAttributes, \
    NicknamesLinks

class NicknameConverter(ApiConverter[Nicknames]):
    @classmethod
    def from_api(cls, data):
        _type = data['type']
        _id = data['id']
        relationships = NicknamesRelationships(**data['relationships'])
        attributes = NicknamesAttributes(**data['attributes'])

        moves = (
            ('self', 'self_'),
        )

        for source, destination in moves:
            data[destination] = data[source]
            del data[source]

        links = NicknamesLinks(**data['links'])
        return Nicknames(
            id=_id,
            type=_type,
            relationships=relationships,
            attributes=attributes,
            links=links
        )

