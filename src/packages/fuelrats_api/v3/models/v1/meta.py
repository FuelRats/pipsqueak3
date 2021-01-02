import pendulum
import attr


@attr.dataclass
class Meta:
    rateLimitTotal: int
    """The total of number requests per hour for the current client"""
    rateLimitRemaining: int
    """The remaining number of requests allowed for this client for the hour"""
    rateLimitReset: pendulum.DateTime
    """Timestamp for when rate limit usage will reset (top of the next hour)"""
    apiVersion: str
    """The current Fuel Rats API version\n"""
