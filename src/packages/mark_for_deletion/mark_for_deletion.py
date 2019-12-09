"""
mark_for_deletion.py - Mark for Deletion object

Provides a class model for the FR API Mark for Deletion(tm) object

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from typing import Optional

import attr


def not_empty(inst, attr, value):
    """ attribute validator asserting `value` is truthy """
    if not value:
        raise TypeError("value must not be empty.")


non_empty_string = attr.validators.and_(attr.validators.instance_of(str), not_empty)


@attr.s(frozen=True, hash=True)
class MarkForDeletion:
    marked: bool = attr.ib(
        validator=attr.validators.instance_of(bool),
        default=False
    )

    reporter: Optional[str] = attr.ib(
        validator=attr.validators.optional(non_empty_string),
        default=None
    )
    reason: Optional[str] = attr.ib(
        validator=attr.validators.optional(non_empty_string),
        default=None
    )
