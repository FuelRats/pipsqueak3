import pydle


class Trigger(object):
    """Object to hold information on the user who invoked a command (and where they did it)."""

    def __init__(self, bot: pydle.BasicClient, nickname: str, target: str, ident: str, hostname: str,
                 realname: str = "", away: str = None, account: str = None, identified: bool = False):
        """
        Object to hold information on the user who invoked a command (and where they did it).\n
        :param bot: Pydle instance
        :type bot: Pydle
        :param nickname: irc nickname of the triggering user
        :type nickname: str
        :param target: target: The message target (usually a channel or, if it was sent in a query window, the bot's
            nick)
        :type target: str
        :param ident: Triggering user's identity
        :type ident: str
        :param hostname: triggering users hostname
        :type hostname: str
        :param realname: users set realname
        :type realname: str
        :param away: Away message
        :type away: str
        :param account: ???
        :type account: str
        :param identified: is the user identified with nickserv?
        :type identified: bool
        """
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
    def from_bot_user(cls, bot: pydle.BasicClient, nickname: str, target: str):
        """
        Creates a `Trigger` object from a user dictionary as used by pydle.
        :param bot: Instance of the bot.
        :param nickname: Command sender's nickname.
        :param target: The message target (usually a channel or, if it was sent in a query window, the bot's nick)
        """
        user = bot.users[nickname]
        return cls(bot, user["nickname"], target,
                   ident=user["username"], hostname=user["hostname"], away=user["away_message"],
                   account=user["account"], identified=user["identified"])

    @property
    def channel(self):
        return self.target if self.bot.is_channel(self.target) else None

    async def reply(self, msg: str):
        """Sends a message in the same channel or query window as the command was sent."""
        await self.bot.message(self.channel if self.channel else self.nickname, msg)
