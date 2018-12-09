from main import MechaClient


class MockBot(MechaClient):
    """Emulates some of the bots functions for testing purposes."""

    def __init__(self, *args, **kwargs):
        # lets ensure the super gets called first, before we start overriding things
        super().__init__(*args, **kwargs)
        self.sent_messages = []
        self.users = {
            "unit_test[bot]": {
                'away': True,
                'away_message': 'Go away',
                'username': 'unit_test',
                'hostname': 'i.see.none',
                'realname': 'you know',
                'identified': True,
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

                "realname": "tree hugger",

            },
            "some_recruit": {
                "nickname": "some_recruit",
                "username": "ident_ed_your_car_sorry_bad_pun",
                "hostname": "recruit.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,

                "realname": "some pun-ter",

            },
            "some_ov": {
                "nickname": "some_ov",
                "username": "ill_stop",
                "hostname": "overseer.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,

                "realname": "Stop sign",

            },
            "some_admin": {
                "nickname": "some_admin",
                "username": "SirRaymondLuxuryYacht",
                "hostname": "admin.fuelrats.com",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,

                "realname": "SirRaymond",

            },
            "authorized_but_not_identified": {
                "nickname": "authorized_but_not_identified",
                "username": "ImHungry",
                "hostname": "i.see.all",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": False,

                "realname": "White Sheets",

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

    async def connect(self):
        """Pydle connect override to prevent the mock accidently connecting to a server"""
        raise RuntimeWarning("Connection to a server disallowed in instances of the mock bot.")
