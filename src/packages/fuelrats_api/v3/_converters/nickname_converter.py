from .links_converter import LinksConverter
from .relationship_converter import RelationshipConveter
from .. import ApiConverter
from .._dataclasses.nicknames import (
    Nicknames,
    NicknamesAttributes,
    NicknamesRelationships,
)


class NicknameConverter(ApiConverter[Nicknames]):
    """
    Converts a "nicknames" type
    """

    @classmethod
    def from_api(cls, data):
        _type = data["type"]
        if _type != "nicknames":
            raise ValueError(f"wrong data type {_type!r}!")
        _id = data["id"]
        relationships = RelationshipConveter.from_api(data["relationships"])
        attributes = NicknamesAttributes(**data["attributes"])

        links = LinksConverter.from_api(data["links"])
        return Nicknames(
            id=_id,
            type=_type,
            relationships=NicknamesRelationships(**relationships),
            attributes=attributes,
            links=links,
        )
