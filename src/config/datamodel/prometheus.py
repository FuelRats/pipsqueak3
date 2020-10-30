from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Union

import attr

IPAddress = Union[IPv6Address, IPv4Address]


@attr.define
class TelemetryConfigRoot:
    bind_host: IPAddress = attr.ib(
        validator=attr.validators.instance_of((IPv4Address, IPv6Address)),
        default=ip_address("127.0.0.1"),
    )
    bind_port: int = attr.ib(validator=attr.validators.instance_of(int), default=6820)
    enabled: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
