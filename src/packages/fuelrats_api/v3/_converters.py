from __future__ import annotations

from uuid import UUID

from loguru import logger

from src.packages.rat import Rat
from src.packages.rescue import Rescue
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
        RENAMES = [
            ("codeRed", "codeRed"),
            ("unidentifiedRats", "unidentified_rats")
        ]
        REMOVES = [
            "data", "createdAt", "updatedAt", "notes",
        ]
        content = data['data']
        uuid = UUID(content['id'])
        attributes = content['attributes']
        logger.debug("original attributes:= {}", attributes)

        for source, destination in RENAMES:
            attributes[destination] = attributes[source]
            del attributes[source]

        for key in REMOVES:
            del attributes[key]

        logger.debug("translated attributes := {}", attributes)
        return Rescue(uuid=uuid, **attributes)

    @classmethod
    def to_api(cls, data: Rescue):
        output = {
            "data":
                {
                    "type": "rescues",
                    "id": f"{data.api_id}",  # cast to string as UUID can't be serialized
                    "attributes": {
                        "client": data.client,
                        "codeRed": data.code_red,
                        "platform": data.platform.value.casefold(),
                        # "quotes": null,  # FIXME: serialize quotes
                        "status": data.status.value,
                        "system": data.system,
                        "title": data.title,
                        # "outcome": null,  # TODO: see if we need to include this
                        # "unidentifiedRats": null,  # FIXME implement unident rat serialziation

                    }}}
        return output
