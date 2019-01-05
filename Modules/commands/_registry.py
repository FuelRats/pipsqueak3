"""
_database.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from collections.abc import MutableMapping
from typing import Callable, Dict, Iterator, List

from ._command import Command

_registry_type: Dict[str, Command] = {}


class Registry(MutableMapping):
    """

    Commands registry.

    This class maintains a registry of registered Command objects.

    This class extends `collections.abc.MutableMapping` and subsequently supports mapping features.

    To demonstrate this, we will define an example command..
    >>> @command('doc_reg_ex0')
    ... async def doc_reg_ex0(*args, **kwargs):
    ...     print("in doc_reg_ex0!")

    Now that our command is registered, it's name can be used as keys into this registry
    >>> registry['doc_reg_ex0'].underlying
    <function doc_reg_ex0 at ...>

    The function is registered as an :class:`Command` object, which also contains information
    about the requested hooks. See :class:`Command` for more.

    """

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


registry = Registry()


def command(*aliases, **kwargs: Dict) -> Callable:
    """
    `@command` decorator

    registers the decorated function as a Command within the commands :obj:`registry`

    Examples:
        Register a plain old command, with no execution hooks
        >>> @command('doc_alias_foo', 'doc_alias_bar')
        ... async def doc_cmd_foo(*args, **kwargs):
        ...     print("in doc_cmd_foo!")

        Once registration is complete, the original function is returned unmodified.
        >>> doc_cmd_foo
        <function doc_cmd_foo at ...>

    Kwargs:
        This function will pass keyword arguments to :class:`Command`'s constructor to enable
        pre-execution and post-execution hooks. see that class for more details



    Args:
        *aliases: string names to register
        **kwargs: keyword arguments to pass to the underlying :class:`Command` constructor

    Returns:
        Callable: decorated function, unmodified.
    """

    def real_decorator(func: Callable):
        cmd = Command(*aliases, underlying=func, **kwargs)
        for alias in aliases:
            assert alias not in registry, f"command with alias '{alias}' already exists!"
            # register each alias
            registry[alias] = cmd
        return func

    return real_decorator
