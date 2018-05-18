import pytest

from Modules.commandcontext import CommandContext


def test_create_manual_channel(bot_fx):
    trigger = CommandContext(bot_fx, ["don't", "care"], ["don't care", "care"], None,
                             target="#somechannel")
    assert trigger.channel == "#somechannel"


def test_create_manual_query(bot_fx):
    trigger = CommandContext(bot_fx, ["don't", "care"], ["don't care", "care"], None,
                             target="#somechannel")
    assert trigger.channel is None


@pytest.mark.asyncio
async def test_create_from_user_channel(bot_fx):
    trigger = await CommandContext.from_bot_user(bot_fx, "unit_test", "#somechannel",
                                           ["some", "thing"], ["some thing", "thing"])
    assert trigger.channel == "#somechannel"

    assert trigger.words == ["some", "thing"]
    assert trigger.words_eol == ["some thing", "thing"]

    assert trigger.user.nickname == bot_fx.users["unit_test"]["nickname"]
    assert trigger.user.ident == bot_fx.users["unit_test"]["username"]
    assert trigger.user.realname is None
    assert trigger.user.hostname == bot_fx.users["unit_test"]["hostname"]
    assert trigger.user.away == bot_fx.users["unit_test"]["away_message"]
    assert trigger.user.account == bot_fx.users["unit_test"]["account"]
    assert trigger.user.identified == bot_fx.users["unit_test"]["identified"]


@pytest.mark.asyncio
async def test_create_from_user_query(bot_fx):
    trigger = await CommandContext.from_bot_user(bot_fx, "unit_test[BOT]", "not_a_channel",
                                           ["some", "thing"], ["some thing", "thing"])
    assert trigger.channel is None

    assert trigger.words == ["some", "thing"]
    assert trigger.words_eol == ["some thing", "thing"]

    assert trigger.user.nickname == bot_fx.users["unit_test[BOT]"]["nickname"]
    assert trigger.user.ident == bot_fx.users["unit_test[BOT]"]["username"]
    assert trigger.user.realname is None
    assert trigger.user.hostname == bot_fx.users["unit_test[BOT]"]["hostname"]
    assert trigger.user.away == bot_fx.users["unit_test[BOT]"]["away_message"]
    assert trigger.user.account == bot_fx.users["unit_test[BOT]"]["account"]
    assert trigger.user.identified == bot_fx.users["unit_test[BOT]"]["identified"]


@pytest.mark.asyncio
async def test_reply_channel(bot_fx):
    trigger = CommandContext(bot_fx, ["some", "thing"], ["some thing", "thing"], None)
    await trigger.reply("Exceedingly smart test message.")
    assert {
               "target": "#somechannel",
               "message": "Exceedingly smart test message."
           } in bot_fx.sent_messages


@pytest.mark.asyncio
async def test_reply_query(bot_fx):
    trigger = CommandContext(bot_fx, ["some", "thing"], ["some thing", "thing"], None)
    await trigger.reply("Exceedingly smart test message.")
    assert {
               "target": "test_nick",
               "message": "Exceedingly smart test message."
           } in bot_fx.sent_messages


def test_trigger_eq(bot_fx):
    trigger1 = CommandContext(bot_fx, ["some", "thing"], ["some thing", "thing"], None,
                              "#unit_test")
    trigger2 = CommandContext(bot_fx, ["some", "thing"], ["some thing", "thing"], None,
                              "#unit_test")

    assert trigger1 == trigger1
    assert trigger2 == trigger2

    assert trigger1 == trigger2
    assert trigger2 == trigger1


def test_trigger_ne(bot_fx):
    trigger1 = CommandContext(bot_fx, ["some", "thing"], ["some thing", "thing"], None,
                              "#unit_test")
    trigger2 = CommandContext(bot_fx, ["some", "thing"], ["another thing", "thing"], None,
                              "#unit_test")

    assert trigger1 != trigger2
    assert trigger2 != trigger1


@pytest.mark.xfail
def test_trigger_hash():
    trigger1 = CommandContext(None, ["some", "thing"], ["some thing", "thing"], None, "#unit_test")
    trigger2 = CommandContext(None, ["some", "thing"], ["some thing", "thing"], None, "#unit_test")
    trigger3 = CommandContext(None, ["some", "thing"], ["another thing", "thing"], None,
                              "#unit_test")

    assert hash(trigger1) == hash(trigger2)
    assert hash(trigger1) != hash(trigger3)
    assert hash(trigger2) != hash(trigger3)
