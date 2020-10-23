from typing import Set

import attr


@attr.dataclass
class PermissionsObj:
    vhosts: Set[str]
    level: int
    denied_message: str = attr.ib(default="Access Denied.")


@attr.dataclass
class PermissionsConfigRoot:
    recruit: PermissionsObj
    rat: PermissionsObj
    overseer: PermissionsObj
    techrat: PermissionsObj
    administrator: PermissionsObj
