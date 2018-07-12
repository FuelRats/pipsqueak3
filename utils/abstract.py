"""
Abstract class from MHajoha's API branch
"""

from abc import abstractmethod
from functools import wraps
from typing import Tuple, Callable


class Abstract(object):
    """
    Base class to create abstract classes without the need for metaclasses (unlike :class:`ABC`),
    allowing the use with other metaclass-based utilities (such as generics).

    The derived class can not be instantiated. Indirect subclasses must either override all abstract
    members or be themselves abstract (by inheriting directly from :class:`Abstract`).

    Examples:
        >>> class MyAbstractClass(Abstract):
        ...     @abstractmethod
        ...     def foo(self): ...
        >>> MyAbstractClass()
        Traceback (most recent call last):
          ...
        TypeError: cannot initialize abstract class MyAbstractClass

        >>> class MyBadlyDerivedClass(MyAbstractClass):
        ...     pass
        Traceback (most recent call last):
          ...
        TypeError: must override abstract members foo or make class MyBadlyDerivedClass itself abstract

        >>> class MyWellDerivedClass(MyAbstractClass):
        ...     def foo(self):
        ...         print("Success!")
        >>> MyWellDerivedClass().foo()
        Success!
    """
    def __init_subclass__(cls):
        abstracts = _get_abstracts(cls)
        if Abstract not in cls.__bases__ and len(abstracts) > 0:
            raise TypeError(f"must override abstract members {', '.join(abstracts)} or make class "
                            f"{cls.__name__} itself abstract")
        else:
            if not getattr(cls.__new__, "_is_abstract_replacement", False):
                cls.__new__ = _abstract_repl_new(cls.__new__)


def _abstract_repl_new(fun: Callable):
    @wraps(fun)
    def wrapper(cls: type, *args, **kwargs):
        if Abstract in cls.__bases__:
            raise TypeError(f"cannot initialize abstract class {cls.__name__}")
        else:
            try:
                return fun(cls, *args, **kwargs)
            except TypeError as te:
                if te.args == ("object() takes no parameters",):
                    return fun(cls)
                else:
                    raise te
    wrapper._is_abstract_replacement = True
    return wrapper


def _get_abstracts(klass: type) -> Tuple[str, ...]:
    # Collect methods
    attrs = {}
    for superclass in reversed(klass.mro()):
        attrs.update(superclass.__dict__)

    # Pick out the names of all abstract attributes
    return tuple(name for name, attr in attrs.items()
                 if getattr(attr, "__isabstractmethod__", False))
