from datetime import datetime

import attr


@attr.dataclass
class Meta:
    rateLimitTotal: int
    rateLimitRemaining: int
    rateLimitReset: datetime
    apiVersion: str
