from .. import ApiConverter
from src.packages.fuelrats_api.v3._dataclasses.jsonapi.link import Link, Links


class LinkCoverter(ApiConverter[Link]):
    """ An individual JSONAPI link object """

    @classmethod
    def from_api(cls, data):
        # https://jsonapi.org/format/#document-links
        if isinstance(data, str):
            # links type A
            return Link(href=data)
        # links type B
        return Link(**data)


class LinksConverter(ApiConverter[Links]):
    """ Converts a link object member list """

    # https://jsonapi.org/format/#document-links
    @classmethod
    def from_api(cls, data):
        return {key: LinkCoverter.from_api(value) for key, value in data.items()}
