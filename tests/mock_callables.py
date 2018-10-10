"""
mocks.py - Mock callables. Objects that can be called and later inquired as to how they were called.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.
"""
import inspect
from typing import List, NamedTuple, Dict, Any, Tuple, Callable, Optional

Call = NamedTuple("_Call", args=tuple, kwargs=Dict[str, Any])


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

    Additionally, a :class:`CallableMock` can be made to mimic an existing function or method, such
    that args and kwargs can be matched to the arguments that the function expects. This also works
    with many other callables including bound methods, but may fail for certain built-in functions
    and methods.

    Note that calling a mock mimicking a function will raise a :exc:`TypeError` if the provided
    arguments don't fit the method. The same restriction also applies to the `was_called_with`
    method on those mock instances.

    >>> def target_function(my_arg): ...
    >>> fun = CallableMock(target_function)
    >>> fun("banana")
    >>> fun.was_called_with("banana")
    True
    >>> fun.was_called_with(my_arg="banana")
    True

    This is not possible when that function is not provided, as args and kwargs will be kept
    separate:

    >>> fun = CallableMock()
    >>> fun("banana")
    >>> fun.was_called_with("banana")
    True
    >>> fun.was_called_with(my_arg="banana")
    False
    """

    def __init__(self, function_to_mimic: Callable = None):
        if function_to_mimic is None:
            self._signature = None
        else:
            self._signature = inspect.signature(function_to_mimic)

        self.return_value = None
        self._calls: List[Call] = []
        self._bound_calls: List[inspect.BoundArguments] = None if function_to_mimic is None else []

    def __call__(self, *args, **kwargs):
        self._calls.append(Call(args, kwargs))
        if self._signature is not None:
            self._bound_calls.append(self._signature.bind(*args, **kwargs))
        return self.return_value

    was_called: bool = property(lambda self: len(self._calls) > 0)
    """
    Was this instance ever called?
    """

    was_called_once: bool = property(lambda self: len(self._calls) == 1)
    """
    Was this instance called exactly once?
    """

    calls: Tuple[Call, ...] = property(lambda self: tuple(self._calls))
    """
    A read-only view of the calls that were made to this object.
    """

    bound_calls: Optional[Tuple[inspect.BoundArguments, ...]] = property(
        lambda self: tuple(self._bound_calls) if self._signature else None)
    """
    A read-only view of the calls bound to the function which this mock mimics.
    None if this mock does not mimic a function.
    """

    def was_called_with(self, *args, **kwargs) -> bool:
        """
        Was this instance called with the given arguments?
        Can take :class:`InstanceOf` objects to check for types.

        Raises:
            TypeError: If this mock callable mimics a real function and *args*, *kwargs* don't fit
                       that function's signature.
        """
        return Call(args, kwargs) in self._calls or \
               self._signature is not None and \
               self._signature.bind(*args, **kwargs) in self._bound_calls

    def reset(self):
        """
        Reset all saved calls to this mock.
        """
        self._calls.clear()


class AsyncCallableMock(CallableMock):
    """
    This is like :class:`CallableMock`, however calling it returns an awaitable coroutine rather
    than the set return value directly.
    """

    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
