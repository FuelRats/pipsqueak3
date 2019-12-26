from .. import ApiConverter
from .._dataclasses.links import Links


class LinksCoverter(ApiConverter[Links]):
    @classmethod
    def from_api(cls, data):
        if "self" in data:
            # links type A
