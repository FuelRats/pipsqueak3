import pytest
from aiounittest import async_test

from Modules.trigger import Trigger
from tests.mock_bot import MockBot

@pytest.fixture
def bot():
    return MockBot()

def test_create_manual_channel(bot):
    trigger = Trigger(bot, "test_nick", "#somechannel", "test_ident", "test.vhost")
    assert trigger.channel == "#somechannel"

def test_create_manual_query(bot):
    trigger = Trigger(bot, "test_nick", "not_a_channel", "test_ident", "test.vhost")
    assert trigger.channel is None

def test_create_from_user_channel(bot):
    trigger = Trigger.from_bot_user(bot, "unit_test", "#somechannel")
    assert trigger.channel == "#somechannel"

    assert trigger.nickname == bot.users["unit_test"]["nickname"]
    assert trigger.ident == bot.users["unit_test"]["username"]
    assert trigger.realname is None
    assert trigger.hostname == bot.users["unit_test"]["hostname"]
    assert trigger.away == bot.users["unit_test"]["away_message"]
    assert trigger.account == bot.users["unit_test"]["account"]
    assert trigger.identified == bot.users["unit_test"]["identified"]

def test_create_from_user_query(bot):
    trigger = Trigger.from_bot_user(bot, "unit_test[BOT]", "not_a_channel")
    assert trigger.channel is None

    assert trigger.nickname == bot.users["unit_test[BOT]"]["nickname"]
    assert trigger.ident == bot.users["unit_test[BOT]"]["username"]
    assert trigger.realname is None
    assert trigger.hostname == bot.users["unit_test[BOT]"]["hostname"]
    assert trigger.away == bot.users["unit_test[BOT]"]["away_message"]
    assert trigger.account == bot.users["unit_test[BOT]"]["account"]
    assert trigger.identified == bot.users["unit_test[BOT]"]["identified"]

@async_test
async def test_reply_channel(bot):
    trigger = Trigger(bot, "test_nick", "#somechannel", "test_ident", "test.vhost")
    await trigger.reply("Exceedingly smart test message.")
    assert {
        "target": "#somechannel",
        "message": "Exceedingly smart test message."
    } in bot.sent_messages

@async_test
async def test_reply_query(bot):
    trigger = Trigger(bot, "test_nick", "not_a_channel", "test_ident", "test.vhost")
    await trigger.reply("Exceedingly smart test message.")
    assert {
        "target": "test_nick",
        "message": "Exceedingly smart test message."
    } in bot.sent_messages
