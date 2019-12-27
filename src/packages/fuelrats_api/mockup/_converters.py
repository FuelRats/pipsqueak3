from __future__ import annotations

import typing
from uuid import UUID

import attr
from loguru import logger

from src.packages.rat import Rat
from src.packages.rescue import Rescue
from src.packages.rescue.internaldata import InternalData as RescueData
from src.packages.utils import Platforms
from src.packages.fuelrats_api._converter import ApiConverter, _DTYPE
from src.packages.mark_for_deletion import MarkForDeletion


class MarkForDeleteConverter(ApiConverter[MarkForDeletion]):
    @classmethod
    def from_api(cls, data):
        return MarkForDeletion(**data)


@attr.s
class InternalDataConverter(ApiConverter[RescueData]):
    mfd_converter: typing.ClassVar[ApiConverter[MarkForDeletion]] = MarkForDeleteConverter

    @classmethod
    def from_api(cls, data):
        return RescueData(
            boardIndex=data['boardIndex'],
            langID=data['langID'],
            markedForDeletion=cls.mfd_converter.from_api(data['markedForDeletion'])
        )

    @classmethod
    def to_api(cls, data: _DTYPE) -> typing.Dict:
        return attr.asdict(data, recurse=True)


class RatConverter(ApiConverter[Rat]):
    @classmethod
    def from_api(cls, data):
        entry = data["data"][0]
        attributes = entry["attributes"]
        uuid = UUID(entry["id"])
        name = attributes["name"]
        platform = Platforms[attributes["platform"].upper()]

        return Rat(uuid=uuid, platform=platform, name=name)


@attr.s
class RescueConverter(ApiConverter[Rescue]):
    internal_data_converter: typing.ClassVar[ApiConverter[RescueData]] = InternalDataConverter

    @classmethod
    def from_api(cls, data):
        renames = [("codeRed", "codeRed"), ("unidentifiedRats", "unidentified_rats")]
        removes = ["data", "createdAt", "updatedAt", "notes", "outcome"]
        content = data["data"]
        uuid = UUID(content["id"])
        attributes = content["attributes"]
        logger.debug("original attributes:= {}", attributes)

        internal_data = cls.internal_data_converter.from_api(attributes['data'])

        attributes["board_index"] = internal_data.boardIndex
        attributes["lang_id"] = internal_data.langID
        attributes["mark_for_deletion"] = internal_data.markedForDeletion

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

        internal_data = RescueData(data.board_index, data.lang_id, {}, data.marked_for_deletion)
        output = {
            "data": {
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
                    "data": attr.asdict(internal_data, recurse=True),
                },
            }
        }
        return output
