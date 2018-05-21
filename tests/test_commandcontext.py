import pytest

from Modules.context import Context
from Modules.user import User


def test_create_manual_channel(bot_fx):
    trigger = Context(bot_fx, ["don't", "care"], ["don't care", "care"], None,
                      target="#somechannel")
    assert trigger.channel == "#somechannel"


def test_create_manual_query(bot_fx):
    trigger = Context(bot_fx, ["don't", "care"], ["don't care", "care"], None,
                      target="somechannel")
    assert trigger.channel is None


@pytest.mark.asyncio
async def test_create_from_user_channel(bot_fx):
    trigger = await Context.from_bot_user(bot_fx, "unit_test", "#somechannel",
                                          ["some", "thing"], ["some thing", "thing"])
    assert trigger.channel == "#somechannel"

    assert trigger.words == ["some", "thing"]
    assert trigger.words_eol == ["some thing", "thing"]

    assert trigger.user.username == bot_fx.users["unit_test"]["username"]
    assert trigger.user.realname == bot_fx.users["unit_test"]["realname"]
    assert trigger.user.hostname == bot_fx.users["unit_test"]["hostname"]
    assert trigger.user.away == bot_fx.users["unit_test"]["away"]
    assert trigger.user.account == bot_fx.users["unit_test"]["account"]
    assert trigger.user.identified == bot_fx.users["unit_test"]["identified"]


@pytest.mark.asyncio
async def test_create_from_user_query(bot_fx):
    trigger = await Context.from_bot_user(bot_fx, "unit_test[BOT]", "not_a_channel",
                                          ["some", "thing"], ["some thing", "thing"])
    assert trigger.channel is None

    assert trigger.words == ["some", "thing"]
    assert trigger.words_eol == ["some thing", "thing"]

    assert trigger.user.username == bot_fx.users["unit_test[BOT]"]["username"]
    assert trigger.user.realname == bot_fx.users["unit_test[BOT]"]["realname"]
    assert trigger.user.hostname == bot_fx.users["unit_test[BOT]"]["hostname"]
    assert trigger.user.away == bot_fx.users["unit_test[BOT]"]["away"]
    assert trigger.user.away_message == bot_fx.users["unit_test[BOT]"]["away_message"]
    assert trigger.user.account == bot_fx.users["unit_test[BOT]"]["account"]
    assert trigger.user.identified == bot_fx.users["unit_test[BOT]"]["identified"]


@pytest.mark.asyncio
async def test_reply_channel(bot_fx):
    trigger = Context(bot_fx, ["some", "thing"], ["some thing", "thing"], None, "#somechannel")
    await trigger.reply("Exceedingly smart test message.")
    assert {
               "target": "#somechannel",
               "message": "Exceedingly smart test message."
           } in bot_fx.sent_messages


@pytest.mark.asyncio
async def test_reply_query(bot_fx):
    user = User("test_nick", "nothing.to.see.here", "test_nick", False, None,
                "moveAlong")
    trigger = Context(bot_fx, ["some", "thing"], ["some thing", "thing"], user, "test_nick")
    await trigger.reply("Exceedingly smart test message.")
    assert {
               "target": "test_nick",
               "message": "Exceedingly smart test message."
           } in bot_fx.sent_messages


def test_trigger_eq(bot_fx):
    trigger1 = Context(bot_fx, ["some", "thing"], ["some thing", "thing"], None,
                       "#unit_test")
    trigger2 = Context(bot_fx, ["some", "thing"], ["some thing", "thing"], None,
                       "#unit_test")

    assert trigger1 == trigger1
    assert trigger2 == trigger2

    assert trigger1 == trigger2
    assert trigger2 == trigger1


def test_trigger_ne(bot_fx):
    trigger1 = Context(bot_fx, ["some", "thing"], ["some thing", "thing"], None,
                              "#unit_test")
    trigger2 = Context(bot_fx, ["some", "thing"], ["another thing", "thing"], None,
                              "#unit_test")

    assert trigger1 != trigger2
    assert trigger2 != trigger1


def test_trigger_hash():
    user = User("foo", "rat.fuelrats.com", "foo", False, None, "foo")
    trigger1 = Context(None, ["some", "thing"], ["some thing", "thing"], user, "#unit_test")
    trigger2 = Context(None, ["some", "thing"], ["some thing", "thing"], user, "#unit_test")
    trigger3 = Context(None, ["some", "thing"], ["another thing", "thing"], user,
                              "#unit_test")

    assert hash(trigger1) == hash(trigger2)
    assert hash(trigger1) != hash(trigger3)
    assert hash(trigger2) != hash(trigger3)
