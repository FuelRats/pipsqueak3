import pydle


class Trigger(object):
    """Object to hold information on the user who invoked a command (and where they did it)."""

    def __init__(self, bot: pydle.BasicClient, nickname: str, target: str, ident: str, hostname: str,
                 realname: str = "", away: str = None, account: str = None, identified: bool = False):
        self.bot = bot
        self.nickname = nickname
        self.target = target
        self.ident = ident
        self.hostname = hostname
        self.realname = realname
        self.away = away
        self.account = account
        self.identified = identified

    @classmethod
    def from_user_dict(cls, bot: pydle.BasicClient, user: dict, target: str):
        """Creates a `Trigger` object from a user dictionary as used by pydle."""
        return cls(bot, user["nickname"], target,
                   ident=user["username"], hostname=user["hostname"], away=user["away_message"],
                   account=user["account"], identified=user["identified"])

    @property
    def channel(self):
        return self.target if self.bot.is_channel(self.target) else None

    async def reply(self, msg: str):
        """Sends a message in the same channel or query window as the command was sent."""
        await self.bot.message(self.channel if self.channel else self.nickname, msg)
