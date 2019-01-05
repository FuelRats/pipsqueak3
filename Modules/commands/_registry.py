"""
_database.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from collections.abc import MutableMapping
from typing import Callable, Dict, Iterator

from ._command import Command

_registry_type: Dict[str, Command] = {}


class Registry(MutableMapping):
    def __init__(self):
        self._commands: Dict[str, Command] = {}

    @property
    def commands(self) -> _registry_type:
        """
        Registered commands.
        """
        return self._commands

    @commands.setter
    def commands(self, value: _registry_type):
        if not isinstance(value, dict):
            raise TypeError(f"value must be a dict, got {type(value)}")
        self._commands = value

    def __setitem__(self, key: str, value: Command) -> None:
        if not isinstance(key, str):
            raise TypeError(f"Registry keys must be of type str. got {type(key)}")

        if not isinstance(value, Command):
            raise TypeError(f"Registry keys must be Command objects. got {type(value)}")

        self.commands[key] = value

    def __delitem__(self, key: str) -> None:
        del self.commands[key]

    def __getitem__(self, key: str) -> Command:
        return self.commands[key]

    def __len__(self) -> int:
        return len(self.items())

    def __iter__(self) -> Iterator[str]:
        return iter(self.commands)


def command(*aliases, **kwargs):
    def real_decorator(func: Callable):
        cmd = Command(*aliases, underlying=func, **kwargs)
