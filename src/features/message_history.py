import typing

from pydle.features.rfc1459.client import RFC1459Support


class MessageHistoryClient(RFC1459Support):
    __slots__ = [
        "__channel_history"
    ]

    def __init__(self, nickname, fallback_nicknames=[], username=None, realname=None, eventloop=None,
                 **kwargs):
        super().__init__(nickname, fallback_nicknames, username, realname, eventloop, **kwargs)
        self.__channel_history: typing.Dict[str, typing.Dict[str, str]] = {}

    async def on_message(self, target, by, message):
        # ensure target exists in tracking
        if target not in self.__channel_history:
            self.__channel_history[target] = {}
        self.__channel_history[target][by] = message

        return await super().on_message(target, by, message)

    def get_last_message(self, channel: str, user: str):
        users = self.__channel_history.get(channel, {})
        return users.get(user)
