import pytest

from Modules.trigger import Trigger

def test_create_manual_channel(bot_fx):
    trigger = Trigger(bot_fx, ["don't", "care"], ["don't care", "care"], "test_nick", "#somechannel",
                      "test_ident", "test.vhost")
    assert trigger.channel == "#somechannel"

def test_create_manual_query(bot_fx):
    trigger = Trigger(bot_fx, ["don't", "care"], ["don't care", "care"], "test_nick", "not_a_channel",
                      "test_ident", "test.vhost")
    assert trigger.channel is None

def test_create_from_user_channel(bot_fx):
    trigger = Trigger.from_bot_user(bot_fx, "unit_test", "#somechannel",
                                    ["some", "thing"], ["some thing", "thing"])
    assert trigger.channel == "#somechannel"

    assert trigger.words == ["some", "thing"]
    assert trigger.words_eol == ["some thing", "thing"]

    assert trigger.nickname == bot_fx.users["unit_test"]["nickname"]
    assert trigger.ident == bot_fx.users["unit_test"]["username"]
    assert trigger.realname is None
    assert trigger.hostname == bot_fx.users["unit_test"]["hostname"]
    assert trigger.away == bot_fx.users["unit_test"]["away_message"]
    assert trigger.account == bot_fx.users["unit_test"]["account"]
    assert trigger.identified == bot_fx.users["unit_test"]["identified"]

def test_create_from_user_query(bot_fx):
    trigger = Trigger.from_bot_user(bot_fx, "unit_test[BOT]", "not_a_channel",
                                    ["some", "thing"], ["some thing", "thing"])
    assert trigger.channel is None

    assert trigger.words == ["some", "thing"]
    assert trigger.words_eol == ["some thing", "thing"]

    assert trigger.nickname == bot_fx.users["unit_test[BOT]"]["nickname"]
    assert trigger.ident == bot_fx.users["unit_test[BOT]"]["username"]
    assert trigger.realname is None
    assert trigger.hostname == bot_fx.users["unit_test[BOT]"]["hostname"]
    assert trigger.away == bot_fx.users["unit_test[BOT]"]["away_message"]
    assert trigger.account == bot_fx.users["unit_test[BOT]"]["account"]
    assert trigger.identified == bot_fx.users["unit_test[BOT]"]["identified"]

@pytest.mark.asyncio
async def test_reply_channel(bot_fx):
    trigger = Trigger(bot_fx, ["some", "thing"], ["some thing", "thing"],
                      "test_nick", "#somechannel", "test_ident", "test.vhost")
    await trigger.reply("Exceedingly smart test message.")
    assert {
        "target": "#somechannel",
        "message": "Exceedingly smart test message."
    } in bot_fx.sent_messages

@pytest.mark.asyncio
async def test_reply_query(bot_fx):
    trigger = Trigger(bot_fx, ["some", "thing"], ["some thing", "thing"],
                      "test_nick", "not_a_channel", "test_ident", "test.vhost")
    await trigger.reply("Exceedingly smart test message.")
    assert {
        "target": "test_nick",
        "message": "Exceedingly smart test message."
    } in bot_fx.sent_messages
