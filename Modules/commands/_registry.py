"""
_registry.py - Defines a registry object for holding commands

Defines a :class:`Registry` class that facilitates

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging
from collections import abc
from typing import Callable, Dict, Iterator

from ._command import Command

_command_registry_type: Dict[str, Command] = {}
LOG = logging.getLogger(f"mecha.{__name__}")


class NameCollision(Exception):
    """
    Alias is already registered.
    """


class Registry(abc.Mapping):
    """

    Commands registry.

    This class maintains a registry of registered Command objects.

    This class extends `collections.abc.MutableMapping` and subsequently supports mapping features.

    >>> registry = Registry()  # setup task

    To demonstrate this, we will define an example command..
    >>> @registry.register('doc_reg_ex0')
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
    def commands(self) -> _command_registry_type:
        """
        Registered commands.
        """
        return self._commands

    @commands.setter
    def commands(self, value: _command_registry_type):
        if not isinstance(value, dict):
            raise TypeError(f"value must be a dict, got {type(value)}")
        self._commands = value

    def __getitem__(self, key: str) -> Command:
        return self.commands[key]

    def __len__(self) -> int:
        return len(self.items())

    def __iter__(self) -> Iterator[str]:
        return iter(self.commands)

    def register(self, *aliases, **kwargs: Dict) -> Callable:
        """
        `@register` decorator

        registers the decorated function as a Command within the commands :obj:`registry`

        Examples:
            Firstly we need a registry to register against,

            >>> registry = Registry()

            Then, we can register a plain old command, with no execution hooks

            >>> @registry.register('doc_alias_foo', 'doc_alias_bar')
            ... async def doc_cmd_foo(*args, **kwargs):
            ...     print("in doc_cmd_foo!")

            Once registration is complete, the original function is returned unmodified.

            >>> doc_cmd_foo
            <function doc_cmd_foo at ...>

            Of course, even though this decorator returns the original, it does store a reference
            to it in the registry.
            >>> registry['doc_alias_foo'].underlying
            <function doc_cmd_foo at ...>

            Please note that command aliases are casefolded, for ease in comparisons.

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

            if not callable(func):
                raise TypeError(f"decorated object must be callable. {func} is not callable.")
            cmd = Command(*aliases, underlying=func, **kwargs)
            for alias in aliases:
                if alias.casefold() in self:
                    raise NameCollision(f"command with alias '{alias}' already exists!")

                LOG.debug(f"registering '{alias.casefold()}' for underlying {func}...")
                # register each alias
                self.commands[alias.casefold()] = cmd
            return func

        return real_decorator
