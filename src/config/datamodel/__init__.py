"""
dataclasses for the configuration system

Copyright (c) 2020 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from ipaddress import ip_address, IPv4Address, IPv6Address

from .prometheus import IPAddress
from .root import ConfigRoot
import cattr

__all__ = ["ConfigRoot"]


def structure_ip_address(raw: str, *args) -> IPAddress:
    return ip_address(raw)


cattr.register_structure_hook(IPAddress, structure_ip_address)
cattr.register_structure_hook(IPv4Address, structure_ip_address)
cattr.register_structure_hook(IPv6Address, structure_ip_address)

cattr.register_unstructure_hook(IPv6Address, lambda data: f"{data}")
cattr.register_unstructure_hook(IPv4Address, lambda data: f"{data}")
