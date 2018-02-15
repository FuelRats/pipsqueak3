import unittest

from aiounittest import async_test

from Modules.trigger import Trigger
from tests.mock_bot import MockBot


class TriggerTests(unittest.TestCase):
    def setUp(self):
        self.bot = MockBot()

    def test_create_manual_channel(self):
        trigger = Trigger(self.bot, "test_nick", "#somechannel", "test_ident", "test.vhost")
        self.assertEqual("#somechannel", trigger.channel)

    def test_create_manual_query(self):
        trigger = Trigger(self.bot, "test_nick", "not_a_channel", "test_ident", "test.vhost")
        self.assertIsNone(trigger.channel)

    def test_create_from_user_channel(self):
        trigger = Trigger.from_bot_user(self.bot, "unit_test", "#somechannel")
        self.assertEqual(trigger.channel, "#somechannel")

        self.assertEqual(trigger.nickname, self.bot.users["unit_test"]["nickname"])
        self.assertEqual(trigger.ident, self.bot.users["unit_test"]["username"])
        self.assertEqual(trigger.realname, "")
        self.assertEqual(trigger.hostname, self.bot.users["unit_test"]["hostname"])
        self.assertEqual(trigger.away, self.bot.users["unit_test"]["away_message"])
        self.assertEqual(trigger.account, self.bot.users["unit_test"]["account"])
        self.assertEqual(trigger.identified, self.bot.users["unit_test"]["identified"])

    def test_create_from_user_query(self):
        trigger = Trigger.from_bot_user(self.bot, "unit_test[BOT]", "not_a_channel")
        self.assertIsNone(trigger.channel)

        self.assertEqual(trigger.nickname, self.bot.users["unit_test[BOT]"]["nickname"])
        self.assertEqual(trigger.ident, self.bot.users["unit_test[BOT]"]["username"])
        self.assertEqual(trigger.realname, "")
        self.assertEqual(trigger.hostname, self.bot.users["unit_test[BOT]"]["hostname"])
        self.assertEqual(trigger.away, self.bot.users["unit_test[BOT]"]["away_message"])
        self.assertEqual(trigger.account, self.bot.users["unit_test[BOT]"]["account"])
        self.assertEqual(trigger.identified, self.bot.users["unit_test[BOT]"]["identified"])

    @async_test
    async def test_reply_channel(self):
        trigger = Trigger(self.bot, "test_nick", "#somechannel", "test_ident", "test.vhost")
        await trigger.reply("Exceedingly smart test message.")
        self.assertIn({
            "target": "#somechannel",
            "message": "Exceedingly smart test message."
        }, self.bot.sent_messages)

    @async_test
    async def test_reply_query(self):
        trigger = Trigger(self.bot, "test_nick", "not_a_channel", "test_ident", "test.vhost")
        await trigger.reply("Exceedingly smart test message.")
        self.assertIn({
            "target": "test_nick",
            "message": "Exceedingly smart test message."
        }, self.bot.sent_messages)
