"""
rat.py - Rat object

Handles the rats cache and provides facilities for managing rats.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""

from typing import Optional
from uuid import UUID

import attr

from ..utils import Platforms


def _name_converter(raw):
    if isinstance(raw, str):
        return raw.casefold()
    return raw


@attr.dataclass(frozen=True, hash=True)
class Rat:
    uuid: UUID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(UUID))
    )
    name: str = attr.ib(
        validator=attr.validators.instance_of(str), converter=_name_converter
    )
    platform: Optional[Platforms] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(Platforms)),
        default=None,
    )

    @property
    def unidentified(self):
        return self.uuid is None

    @property
    def identified(self):
        return not self.unidentified
