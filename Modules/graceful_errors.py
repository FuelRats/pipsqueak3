"""
graceful_errors.py - provides facilities for graceful error handling

Users shouldn't see the actual exception raised from a command invocation,
    rather they should see something more lighthearted and mundane

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from typing import Dict

by_error: Dict[type(Exception), str] = {
    ZeroDivisionError: "Rotten.cheddar!",
    TypeError: "Cheddar.rottenCheese! ",
}
