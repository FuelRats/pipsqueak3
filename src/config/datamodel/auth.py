"""
IRC authentication configuration datamodel

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from enum import Enum
from typing import Optional

import attr


@attr.dataclass
class AuthExternalConfig:
    """ External authentication configuration """

    tls_client_cert: str = attr.ib(validator=attr.validators.instance_of(str), default="./none")


class AuthenticationMethod(Enum):
    """ Enum of valid configuration options"""

    NO_AUTH = "NO_AUTH"
    PLAIN = "PLAIN"
    EXTERNAL = "EXTERNAL"


@attr.dataclass
class AuthPlainConfig:
    username: str = attr.ib(validator=attr.validators.instance_of(str))
    password: str = attr.ib(validator=attr.validators.instance_of(str))
    identity: str = attr.ib(validator=attr.validators.instance_of(str))


@attr.dataclass
class AuthenticationConfigRoot:
    method: AuthenticationMethod
    plain: Optional[AuthPlainConfig]
    external: Optional[AuthExternalConfig]
