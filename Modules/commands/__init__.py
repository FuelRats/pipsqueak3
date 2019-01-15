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
    >>> @command_registry.register('alias1', 'alias2')
    ... async def doc_alias1(context:Context):
    ...     print("in doc_alias1")

    This registration will do a couple things for you in the background.

    Most notably it will register a command object for each alias you have specified in the
    registry
    >>> 'alias1' in command_registry and "alias2" in command_registry
    True


    Using this decorator does not change the decorated, so it can be safely called elsewhere without
    complications.
    >>> doc_alias1
    <function doc_alias1 at ...>

    To have your command be guarded by an execution hook, assign the hook **by name** a value.
    Please note many hooks will use the assigned value for specific functions, unless you need to
    change their default behavior, please assign :obj:`ENABLED` as the argument's value.

    >>> @command_registry.register('doc_alias3', require_dm=ENABLED)
    ... async def cmd_alias3(context:Context):
    ...     ...

    If we peak at the registered hooks we will see require_dm has had its hook added.
    >>> command_registry['doc_alias3'].hooks
    [RequireDirectMessageHook(message='this MUST be executed from a direct message with me!')]


    For more information, see the Corresponding hook implementations.





Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from ._command import ENABLED
from ._feature import CommandSupport, RuleSupport, command_registry
from ._hooks import hook, HookImplementation
from ._registry import NameCollision

__all__ = [
    'command_registry',
    'hook',
    'HookImplementation',
    'ENABLED',
    'CommandSupport',
    'RuleSupport',
    'NameCollision'
]
