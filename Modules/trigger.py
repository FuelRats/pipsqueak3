import pydle


class Trigger(object):
    """Object to hold information on the user who invoked a command (and where
    they did it)."""

    def __init__(self, bot: pydle.BasicClient, nickname: str, target: str,
                 ident: str, hostname: str, realname: str = "",
                 away: str = None, account: str = None,
                 identified: bool = False):
        """
        Object to hold information on the user who invoked a command

        Args:
            bot (Pydle): Mecha bot instance
            nickname (str): irc nickname of the triggering user
            target (str): The message target (usually a channel or, if it was
            sent in a query window: the bot's nick)
            ident (str): Triggering user's identity
            hostname (str): triggering users hostname
            realname (str): users defined realname
            away (str): away message
            account (str): ???
            identified (bool): is the user identified via NS?
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
    def from_bot_user(cls, bot: pydle.BasicClient, nickname: str, target: str)\
            -> 'Trigger':
        """
        Creates a `Trigger` object from a user dictionary as used by pydle.

        Args:
            bot (pydle.BasicClient): instance of the bot
            nickname (str): Command sender's nickname.
            target (str): The message target  (usually a channel or, if it was
                sent in a query window, the bot's nick)

        Returns:
            Trigger
        """
        user = bot.users[nickname]
        return cls(bot, user["nickname"], target,
                   ident=user["username"], hostname=user["hostname"],
                   away=user["away_message"], account=user["account"],
                   identified=user["identified"])

    @property
    def channel(self)->str or None:
        """
        The channel the trigger came from.

        Returns:
            str : channel, if it exists
        """
        return self.target if self.bot.is_channel(self.target) else None

    async def reply(self, msg: str):
        """
        Sends a message in the same channel or query window as the command was
        sent.

        Args:
            msg (str): message to send

        Returns:

        """
        await self.bot.message(self.channel if self.channel else self.nickname,
                               msg)

