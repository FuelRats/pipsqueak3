from typing import List, Type, Dict, Union
from uuid import UUID

import cattr
import attr
from ..models.v1.rescue import Rescue as ApiRescue


@attr.dataclass
class RescueUpdate:
    """
    API Rescue Update event
    """

    event: str = attr.ib(validator=attr.validators.instance_of(str))
    state: UUID = attr.ib(validator=attr.validators.instance_of(UUID))
    obj_id: UUID = attr.ib(validator=attr.validators.instance_of(UUID))
    data: Dict = attr.ib(validator=attr.validators.instance_of(dict), factory=dict)


@attr.dataclass
class RescueCreate:
    """ Rescue creation event """
    event: str = attr.ib(validator=attr.validators.instance_of(str))
    state: UUID = attr.ib(validator=attr.validators.instance_of(UUID))
    obj_id: UUID = attr.ib(validator=attr.validators.instance_of(UUID))
    rescue: ApiRescue = attr.ib(validator=attr.validators.instance_of(ApiRescue))


@attr.dataclass
class ConnectionEvent:
    """
    API Connection Event
    """
    event: str = attr.ib(validator=attr.validators.instance_of(str))
    state: int = attr.ib(validator=attr.validators.instance_of(int))
    data: Dict = attr.ib(validator=attr.validators.instance_of(dict), factory=dict)
    data2: Dict = attr.ib(validator=attr.validators.instance_of(dict), factory=dict)


CLS_FOR_EVENT: Dict[str, Type] = {
    'fuelrats.rescueupdate': RescueUpdate,
    'fuelrats.rescuecreate': RescueCreate,
    'connection': ConnectionEvent
}
