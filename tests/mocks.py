"""
mocks.py - Small, miscellaneous mock classes.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.
"""
from typing import List, NamedTuple, Dict, Any


_Call = NamedTuple("_Call", args=tuple, kwargs=Dict[str, Any])


class InstanceOf(object):
    """
    Simple wrapper around a class. To be used in conjunction with :class:`CallableMock` instances.
    Instances of :class:`InstanceOf` compare equal with instances of their wrapped type.

    Examples:
        >>> InstanceOf(str) == "hello"
        True
        >>> InstanceOf(dict) == 7
        False
    """
    __slots__ = ("klass",)

    def __init__(self, klass: type):
        self.klass = klass

    def __eq__(self, other):
        if isinstance(other, self.klass):
            return True
        elif isinstance(other, InstanceOf):
            return self.klass is other.klass
        else:
            return NotImplemented


class CallableMock(object):
    """
    Similar to unittest's MagicMock, this class is callable. It allows the user to set a return
    value and to inquire after the fact what it has been called with.

    Examples:
        >>> fun = CallableMock()
        >>> fun(1, 2, 3, her="lo")
        >>> fun.was_called
        True
        >>> fun.was_called_once
        True
        >>> fun.was_called_with(1, 2, 3, her="lo")
        True
        >>> fun.was_called_with(3, 2, "herlo")
        False
        >>> fun.was_called_with(InstanceOf(int), 2, 3, her=InstanceOf(str))
        True
    """
    def __init__(self):
        self.return_value = None
        self._calls: List[_Call] = []

    def __call__(self, *args, **kwargs):
        self._calls.append(_Call(args, kwargs))
        return self.return_value

    was_called: bool = property(lambda self: len(self._calls) > 0)
    """
    Was this instance ever called?
    """

    was_called_once: bool = property(lambda self: len(self._calls) == 1)
    """
    Was this instance called exactly one?
    """

    def was_called_with(self, *args, **kwargs) -> bool:
        """
        Was this instance called with the given arguments?
        Can take :class:`InstanceOf` objects to check for types.
        """
        return _Call(args, kwargs) in self._calls


class AsyncCallableMock(CallableMock):
    """
    This is like :class:`CallableMock`, however calling it returns an awaitable coroutine rather
    than the set return value directly.
    """
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
