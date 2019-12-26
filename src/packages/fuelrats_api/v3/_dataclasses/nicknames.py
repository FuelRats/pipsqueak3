import attr


@attr.dataclass
class NicknamesAttributes:
    lastQuit: str
    lastRealHost: str
    lastSeen: str


@attr.dataclass
class Nicknames:
    id: int
    attributes: Dict

    type: str = "nicknames"
