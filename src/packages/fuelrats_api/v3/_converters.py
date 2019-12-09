from __future__ import annotations

from uuid import UUID

import attr
from loguru import logger

from src.packages.rat import Rat
from src.packages.rescue import Rescue
from src.packages.rescue.data import Data as RescueData
from src.packages.utils import Platforms
from .._converter import ApiConverter


class RatConverter(ApiConverter[Rat]):
    @classmethod
    def from_api(cls, data):
        entry = data['data'][0]
        attributes = entry['attributes']
        uuid = UUID(entry['id'])
        name = attributes['name']
        platform = Platforms[attributes['platform'].upper()]

        return Rat(uuid=uuid, platform=platform, name=name)


class RescueConverter(ApiConverter[Rescue]):
    @classmethod
    def from_api(cls, data):
        renames = [
            ("codeRed", "codeRed"),
            ("unidentifiedRats", "unidentified_rats")
        ]
        removes = [
            "data", "createdAt", "updatedAt", "notes", "outcome"
        ]
        content = data['data']
        uuid = UUID(content['id'])
        attributes = content['attributes']
        logger.debug("original attributes:= {}", attributes)

        # some fields have different names in the API
        for source, destination in renames:
            attributes[destination] = attributes[source]
            del attributes[source]
        # some fields we don't / cannot want to send to the API at all.
        for key in removes:
            del attributes[key]

        logger.debug("translated attributes := {}", attributes)
        return Rescue(uuid=uuid, **attributes)

    @classmethod
    def to_api(cls, data: Rescue):

        internal_data = RescueData(data.board_index, data.lang_id, {},
                                   data.marked_for_deletion)
        output = {
            "data":
                {
                    "type": "rescues",
                    "id": f"{data.api_id}",  # cast to string as UUID can't be serialized
                    "attributes": {
                        "client": data.client,
                        "codeRed": data.code_red,
                        "platform": data.platform.value.casefold(),  # lowercase in API
                        # "quotes": null,  # FIXME: serialize quotes
                        "status": data.status.value,
                        "system": data.system,
                        "title": data.title,
                        # "outcome": null,  # TODO: see if we need to include this
                        "unidentifiedRats": [],  # FIXME implement unident rat serialziation
                        "data": attr.asdict(internal_data, recurse=True)
                    }}}
        return output
