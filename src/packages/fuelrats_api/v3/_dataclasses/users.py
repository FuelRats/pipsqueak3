import attr

from src.packages.fuelrats_api.v3._dataclasses.relationships import Relationship


@attr.dataclass
class UsersRelationships:
    rats: Relationship
    displayRat: Relationship
    groups: Relationship
    clients: Relationship
    links: Relationship