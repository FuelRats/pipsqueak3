class MockBot(object):
    """Emulates some of the bots functions for testing purposes."""

    def __init__(self):
        self.sent_messages = []
        self.users = {
            "unit_test[BOT]": {'oper': False,
                               'idle': 0,
                               'away': True,
                               'away_message': 'Go away',
                               'username': 'unit_test',
                               'hostname': 'i.see.none',
                               'realname': 'you know',
                               'identified': True,
                               'server': 'irc.fuelrats.com',
                               'server_info': 'Fuel Rat IRC Server',
                               'secure': True,
                               'account': None,
                               'nickname': 'unit_test[BOT]'},
            "unit_test": {
                "nickname": "unit_test",
                "username": "unit_test",
                "hostname": "i.see.only.lemon.trees",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": False,
                "oper": False,
                "idle": 0,
                "realname": "tree hugger",
                "secure": False,
                "server": "irc.fuelrats.com",
                "server_info": "Fuel Rat IRC server"
            },
            "some_recruit": {
                "nickname": "some_recruit",
                "username": "ident_ed_your_car_sorry_bad_pun",
                "hostname": "recruit.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "oper": False,
                "idle": 0,
                "realname": "some pun-ter",
                "secure": False,
                "server": "irc.fuelrats.com",
                "server_info": "Fuel Rat IRC server"
            },
            "some_ov": {
                "nickname": "some_ov",
                "username": "ill_stop",
                "hostname": "overseer.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "oper": False,
                "idle": 0,
                "realname": "Stop sign",
                "secure": False,
                "server": "irc.fuelrats.com",
                "server_info": "Fuel Rat IRC server"
            },
            "some_admin": {
                "nickname": "some_admin",
                "username": "SirRaymondLuxuryYacht",
                "hostname": "admin.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "oper": True,
                "idle": 0,
                "realname": "SirRaymond",
                "secure": True,
                "server": "irc.fuelrats.com",
                "server_info": "Fuel Rat IRC server"
            },
            "authorized_but_not_identified": {
                "nickname": "authorized_but_not_identified",
                "username": "ImHungry",
                "hostname": "i.see.all",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": False,
                "oper": False,
                "idle": 0,
                "realname": "White Sheets",
                "secure": False,
                "server": "irc.fuelrats.com",
                "server_info": "Fuel Rat IRC server"
            }
        }

    async def message(self, target: str, message: str):
        self.sent_messages.append({
            "target": target,
            "message": message
        })

    async def whois(self, name: str) -> dict:
        if name in self.users:
            return self.users[name]

    @classmethod
    def is_channel(cls, channel: str):
        return channel[0] in ("#", "&")
