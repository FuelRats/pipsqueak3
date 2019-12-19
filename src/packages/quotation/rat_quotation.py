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

from ..context import Context


@attr.dataclass
class Quotation:
    """
    A quotes object, element of Rescue

    message (str): quoted message
    author (str): Author of message
    created_at (datetime): time quote first created
    updated_at (datetime): time quote last modified
    last_author (str): last user to modify the quote
    """
    message: str = attr.ib(validator=attr.validators.instance_of(str))
    """ Quote payload """
    author: str = attr.ib(
        validator=attr.validators.instance_of(str),
        default="Mecha")
    """ Original author of quotation """
    last_author: str = attr.ib(
        validator=attr.validators.instance_of(str),
        default="Mecha")
    """ Nickname of the last user to modify this rescue """
    created_at: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime),
        factory=functools.partial(datetime.now, tz=timezone.utc)
    )
    """ Initial creation time """
    updated_at: datetime = attr.ib(
        validator=attr.validators.instance_of(datetime),
        factory=functools.partial(datetime.now, tz=timezone.utc)
    )
    """ Last modification time """

    @contextlib.contextmanager
    def modify(self, context: Context):
        """
        Helper context manager for modifying a quote

        Args:
            context (Trigger): Trigger object of invoking user

        Raises:
            TypeError: modified rescue failed validation
        """
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
