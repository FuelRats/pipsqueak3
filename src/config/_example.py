"""
hooks -   # FIXME teplates



Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import abc
from abc import abstractmethod

import pluggy

hookspec = pluggy.HookspecMarker("myproject")
hookimpl = pluggy.HookimplMarker("myproject")

import sys


_this_module  = sys.modules[__name__]
class MySpec(object):
    """A hook specification namespace.
    """

    @hookspec
    def myhook(self, arg1, arg2):
        """My special little hook that you can customize.
        """
        print("in hookspec")

class MyPluginABC(abc.ABC):
    @abstractmethod
    @hookimpl
    def myhook(self, arg1, arg2):
        ...


class Plugin_1(MyPluginABC):
    """A hook implementation namespace.
    """

    @hookimpl
    def myhook(self, arg1, arg2):
        print("inside Plugin_1.myhook()")
        return arg1 + arg2


class Plugin_2(MyPluginABC):
    """A 2nd hook implementation namespace.
    """

    @hookimpl
    def myhook(self, arg1, arg2):
        print("inside Plugin_2.myhook()")
        return arg1 - arg2

@hookimpl
def myhook(arg1, arg2):
    print("in static myhook")

class Plugin3(MyPluginABC):
    @staticmethod
    @hookimpl
    def myhook( arg1, arg2):
        print("in plugin3.myhook")



# create a manager and add the spec
pm = pluggy.PluginManager("myproject")
pm.add_hookspecs(MySpec)

# register plugins
pm.register(Plugin_1())
pm.register(Plugin_2())
pm.register(_this_module)
pm.register(Plugin3)

# call our ``myhook`` hook
results = pm.hook.myhook(arg1=1, arg2=2)
print(results)