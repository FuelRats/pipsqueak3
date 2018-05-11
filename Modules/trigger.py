from typing import List

import pydle


class Trigger(object):
    """
    Object to hold information on the user who invoked a command as well as where and how the
    command was invoked.
    """

    def __init__(self, bot: pydle.BasicClient, words: List[str], words_eol: List[str],
                 nickname: str, target: str, ident: str, hostname: str, realname: str = None,
                 away: str = None, account: str = None, identified: bool = False):
        """
        Initializes a new `Trigger` object with the provided info.

        Arguments:
            bot (pydle.BasicClient): This bot's instance.
            words ([str]): List of all the words of the message which invoked the command. Does not
                include the command prefix char.
            words_eol ([str]): Same as *words* above, but each element including the word and
                everything up to the end of the message.
            nickname (str): IRC nickname of the triggering user.
            target (str): The message target (a channel or the bot's nick, if it was sent in a query
                window).
            ident (str): Indent of the triggering user (aka username).
            hostname (str): Hostname from which the triggering user is connecting, or their vhost.
            realname (str): Realname defined by the user.
            away (str): The user's away message if they are marked away, None if they are not.
            account (str): Who the user is logged in as. Should be their NickServ username / main
                nickname.
            identified (bool): Whether or not the user is identified with NickServ.
        """
        self.bot = bot
        self.words = words
        self.words_eol = words_eol
        self.nickname = nickname
        self.target = target
        self.ident = ident
        self.hostname = hostname
        self.realname = realname
        self.away = away
        self.account = account
        self.identified = identified



    @classmethod
    def from_bot_user(cls, bot: pydle.BasicClient, nickname: str, target: str, words: List[str],
                      words_eol: List[str] = None) -> 'Trigger':
        """
        Creates a `Trigger` object from a user dictionary as used by pydle.

        Arguments:
            bot (pydle.BasicClient): This bot's instance.
            nickname (str): Command sender's nickname.
            target (str): The message target (usually a channel or, if it was sent in a query
                window, the bot's nick).
            words ([str]): List of all the words of the message which invoked the command. Does not
                include the command prefix char.
            words_eol ([str]): Same as *words* above, but each element including the word and
                everything up to the end of the message.

        Returns:
            Trigger: Object constructed from the provided info.
        """
        user = bot.users[nickname]
        return cls(bot, words=words, words_eol=words_eol, nickname=user["nickname"], target=target,
                   ident=user["username"], hostname=user["hostname"], away=user["away_message"],
                   account=user["account"], identified=user["identified"])

    @property
    def channel(self) -> str or None:
        """
        If the message was sent in a channel, this will be its name and `None` otherwise.
        """
        return self.target if self.bot.is_channel(self.target) else None

    async def reply(self, msg: str):
        """
        Sends a message in the same channel or query window as the command was sent.

        Arguments:
            msg (str): Message to send.
        """
        await self.bot.message(self.channel if self.channel else self.nickname, msg)
