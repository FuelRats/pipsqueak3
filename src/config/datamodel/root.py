from typing import List

import attr

from .auth import AuthenticationConfigRoot
from .board import BoardConfigRoot
from .permissions import PermissionsConfigRoot
from .irc import IRCConfigRoot
from .gelf import LoggingConfigRoot
from .database import DatabaseConfigRoot
from .commands import CommandsConfigRoot
from .api import FuelratsApiConfigRoot, StarsystemApiConfigRoot
from .ratmamma import RatmamaConfigRoot


@attr.dataclass
class ConfigRoot:
    """ Root Mechasqueak configuration object """

    irc: IRCConfigRoot
    authentication: AuthenticationConfigRoot
    permissions: PermissionsConfigRoot
    board: BoardConfigRoot
    logging: LoggingConfigRoot
    database: DatabaseConfigRoot
    commands: CommandsConfigRoot
    api: FuelratsApiConfigRoot
    system_api: StarsystemApiConfigRoot
    ratsignal_parser: RatmamaConfigRoot
