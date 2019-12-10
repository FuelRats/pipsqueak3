import typing

import attr

from ..mark_for_deletion import MarkForDeletion


@attr.s
class InternalData:
    """
    Mecha-internal Rescue data, stored in the
    API ['attributes']['data'] field
    of the API Rescue object.
    """

    boardIndex: int = attr.ib(validator=attr.validators.instance_of(int))
    langID: str = attr.ib(validator=attr.validators.instance_of(str), default="en")
    status: typing.Dict = attr.ib(default=attr.Factory(dict))
    markedForDeletion: MarkForDeletion = attr.ib(
        validator=attr.validators.instance_of(MarkForDeletion),
        default=attr.Factory(MarkForDeletion),
    )
