"""
__init__.py - Commands registry

This package contains the various tools required to define a command.

All you really need to define a command is to use the `@command` decorator, the system will handle
the rest.

Implements:
    collections.abc.MutableMapping
Examples:
    To define a command, its rather straight forward. you pass it an arbitry number of aliases
    you want to register, and use keyword arguments to define what modifiers to apply
    >>> from Modules.context import Context
    >>> @command('alias1', 'alias2')
    ... async def doc_alias1(context:Context):
    ...     print("in doc_alias1")

    This registration will do a couple things for you in the background.

    Most notably it will register a command object for each alias you have specified in the
    registry
    >>> 'alias1' in registry and "alias2" in registry
    True


    Using this decorator does not change the decorated, so it can be safely called elsewhere without
    complications.
    >>> doc_alias1
    <function doc_alias1 at ...>



Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from ._registry import registry, command

__all__ = ['command', 'registry']
