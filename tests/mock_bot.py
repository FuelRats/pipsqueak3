class MockBot(object):
    """Emulates some of the bots functions for testing purposes."""
    async def whois(self, name:str)->dict:
        return self.users[name] if name in self.users else None

    users = {
        "unit_test[BOT]": {
            "nickname": "unit_test[BOT]",
            "username": "unit_test",
            "realname": "unit_test",
            "hostname": "unit_test@i.see.none",
            "away": True,
            "away_message": "Go away",
            "account": "unit_test",
            "identified": True

        },

        "unit_test": {
            "nickname": "unit_test",
            "username": "unit_test",
            "hostname": "unit_test@i.see.only.lemon.trees",
            "realname": "unit_test",
            "away": False,
            "away_message": None,
            "account": None,
            "identified": False
        },
        "some_recruit": {
            "nickname": "some_recruit",
            "username": "ident_ed_your_car_sorry_bad_pun",
            "hostname": "some_recruit@recruit.fuelrats.com",
            "realname": "some_recruit",
            "away": False,
            "away_message": None,
            "account": "some_recruit",
            "identified": True
        },
        "some_ov": {
            "nickname": "some_ov",
            "realname": "some_ov",
            "username": "ill_stop",
            "hostname": "some_ov@overseer.fuelrats.com",
            "away": False,
            "away_message": None,
            "account": "some_ov",
            "identified": True
        },
        "some_admin": {
            "nickname": "some_admin",
            "username": "SirRaymondLuxuryYacht",
            "hostname": "admin.fuelrats.com",
            "realname": "some_admin",
            "away": False,
            "away_message": None,
            "account": "some_admin",
            "identified": True
        },
        "authorized_but_not_identified": {
            "nickname": "authorized_but_not_identified",
            "username": "ImHungry",
            "hostname": "i.see.all",
            "realname": "totallyNotOrange",
            "away": False,
            "away_message": None,
            "account": None,
            "identified": False
        }
    }
    def __init__(self):
        self.sent_messages = []


    async def message(self, target: str, message: str):
        self.sent_messages.append({
            "target": target,
            "message": message
        })

    @classmethod
    def is_channel(cls, channel: str):
        return channel[0] in ("#", "&")
