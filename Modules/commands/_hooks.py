"""
_hooks.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from logging import getLogger

from Modules.context import Context
from Modules.permissions import Permission

LOG = getLogger(f"mecha.{__name__}")

STOP_EXECUTION = object()
"""
Stop execution of this command/rule.

This sentinel should only be returned by pre-execution hooks that want to prevent the underlying
from being invoked. it is ignored outside pre-execution hooks.
"""


class CancelExecution(Exception):
    """
    Raised when a setup hook wants to cancel execution
    """
    ...


# #######
# pre-execute hooks
# #

async def require_channel(context: Context, *args, **kwargs):
    LOG.debug("in require_channel")
    raise CancelExecution("nope!")


async def require_direct_message(context: Context, *args, **kwargs):
    LOG.debug("in require_direct_message")
    return {'dm': True}


async def require_permission(context: Context, permission: Permission, *args, **kwargs):
    LOG.debug("in require_permission")
    ...

# #######
# post-execute hooks
# #
