"""
rat_quotation.py - Rat Quotations

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""

import contextlib
import functools
from datetime import datetime, timezone

import attr
from loguru import logger

from src.packages.context import Context


@attr.dataclass
class Quotation:
    message: str = attr.ib(validator=attr.validators.instance_of(str))
    author: str = attr.ib(
        validator=attr.validators.instance_of(str),
        default="Mecha")
    last_author: str = attr.ib(
        validator=attr.validators.instance_of(str),
        default="Mecha")
    created_at: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime),
        factory=functools.partial(datetime.now, tz=timezone.utc)
    )
    updated_at: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime),
        factory=functools.partial(datetime.now, tz=timezone.utc)
    )

    @contextlib.contextmanager
    def modify(self, context: Context):
        data = attr.asdict(self)

        yield self
        self.last_author = context.user.nickname
        self.updated_at = datetime.now(tz=timezone.utc)

        try:
            attr.validate(self)
        except TypeError:
            logger.warning("failed to validate {}", self)
            for key, value in data.items():
                # since we can't overwrite self we will need to roll back one by one
                setattr(self, key, value)
            raise
        # class Quotation:
