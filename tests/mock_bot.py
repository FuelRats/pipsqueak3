class MockBot(object):
    """Emulates some of the bots functions for testing purposes."""
    def __init__(self):
        self.sent_messages = []

        self.users = {
            "unit_test[BOT]": {
                "nickname": "unit_test[BOT]",
                "username": "unit_test",
                "hostname": "i.see.none",
                "away": True,
                "away_message": "Go away",
                "account": None,
                "identified": True
            },
            "unit_test": {
                "nickname": "unit_test",
                "username": "unit_test",
                "hostname": "i.see.only.lemon.trees",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": False
            },
            "some_recruit": {
                "nickname": "some_recruit",
                "username": "ident_ed_your_car_sorry_bad_pun",
                "hostname": "recruit.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True
            },
            "some_ov": {
                "nickname": "some_ov",
                "username": "ill_stop",
                "hostname": "overseer.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True
            },
            "some_admin": {
                "nickname": "some_admin",
                "username": "SirRaymondLuxuryYacht",
                "hostname": "admin.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True
            },
            "authorized_but_not_identified": {
                "nickname": "authorized_but_not_identified",
                "username": "ImHungry",
                "hostname": "i.see.all",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": False
            }
        }

    async def message(self, target: str, message: str):
        self.sent_messages.append({
            "target": target,
            "message": message
        })

    @classmethod
    def is_channel(cls, channel: str):
        return channel[0] in ("#", "&")
