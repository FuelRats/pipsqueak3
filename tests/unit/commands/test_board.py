from uuid import uuid4

import pytest

from src.packages.context import Context
from src.commands import case_management
from src.packages.rat import Rat
from src.packages.rescue import Rescue
from src.packages.utils import Platforms
from src.packages.commands.rat_command import trigger

pytestmark = [pytest.mark.unit, pytest.mark.commands, pytest.mark.asyncio]


@pytest.mark.parametrize("initial, expected", [(False, True), (True, False)])
async def test_active(rat_board_fx, bot_fx, initial: bool, expected: bool):
    case = await bot_fx.board.create_rescue(client="snafu", active=initial)
    ctx = await Context.from_message(bot_fx, "#unkn0wndev", "some_ov", f"!active {case.board_index}")

    await trigger(ctx)

    assert case.active is expected, "active command failed to behave as expected"


@pytest.mark.parametrize("names", [("foo", "bar", "baz"), ("snafu",)])
async def test_assign_unidentified(rescue_sop_fx, bot_fx, names):
    await bot_fx.board.append(rescue_sop_fx)
    ctx = await Context.from_message(
        bot=bot_fx,
        channel="#unkn0wndev",
        sender="some_ov",
        message=f"!assign {rescue_sop_fx.board_index} {' '.join(names)}",
    )
    await trigger(ctx)
    for name in names:
        assert name in rescue_sop_fx.unidentified_rats, "failed to assign unidentified rats"

    # verify unassign behavior while we are here (less duplication than a distinct test)
    ctx = await Context.from_message(
        bot=bot_fx,
        channel="#unkn0wndev",
        sender="some_ov",
        message=f"!unassign {rescue_sop_fx.board_index} {' '.join(names)}",
    )
    await trigger(ctx)
    for name in names:
        assert name not in rescue_sop_fx.unidentified_rats, "failed to unassign unidentified rats"


async def test_clear_no_rat(rescue_sop_fx, bot_fx):
    await bot_fx.board.append(rescue_sop_fx)
    ctx = await Context.from_message(
        bot_fx, "#unkn0wndev", "some_ov", f"!clear {rescue_sop_fx.board_index}"
    )
    await trigger(ctx)
    assert rescue_sop_fx.board_index not in bot_fx.board, "failed to clear rescue"


async def test_clear_invalid(bot_fx):
    rescue = await bot_fx.board.create_rescue(
        uuid=uuid4(), client="no_cheese_no_life", active=True, system=None, platform=None,
    )
    ctx = await Context.from_message(bot_fx, "#unkn0wndev", "some_ov", f"!clear {rescue.board_index}")
    await trigger(ctx)

    # neither rescue nor platform are set
    assert rescue.board_index in bot_fx.board, "unexpectedly cleared rescue"
    assert bot_fx.sent_messages, "bot failed to reply to user"
    message = bot_fx.sent_messages.pop()["message"].casefold()
    assert "cannot comply" in message, "failed to give correct error message"
    async with bot_fx.board.modify_rescue(rescue) as case:
        case: Rescue
        case.system = "Ki"

    # platform not set

    await trigger(ctx)
    assert rescue.board_index in bot_fx.board, "unexpectedly cleared rescue"
    message = bot_fx.sent_messages.pop()["message"].casefold()
    assert "cannot comply" in message, "failed to bail out"
    assert "platform" in message, "failed to give correct error message"

    # unidentified rat
    async with bot_fx.board.modify_rescue(rescue) as case:
        case: Rescue
        case.unidentified_rats["jack_the_ripper[pc]"] = Rat(None, name="jack")
        case.platform = Platforms.PS

    ctx = await Context.from_message(
        bot_fx, "#unkn0wndev", "some_ov", f"!clear {rescue.board_index} jack_the_ripper[pc]",
    )

    await trigger(ctx)
    assert rescue.board_index in bot_fx.board, "unexpectedly cleared rescue"
    message = bot_fx.sent_messages.pop()["message"].casefold()
    assert "cannot comply" in message, "failed to bail out"
    assert "unidentified" in message, "failed to give correct error message"


async def test_cmd_cmdr(bot_fx, rescue_sop_fx):
    await bot_fx.board.append(rescue_sop_fx)
    ctx = await Context.from_message(
        bot_fx, "#unkn0wndev", "some_ov", f"!cmdr {rescue_sop_fx.board_index} squidface"
    )

    await trigger(ctx)
    assert rescue_sop_fx.client == "squidface", "failed to assign commander"
    message = bot_fx.sent_messages.pop()["message"].casefold()
    assert "is now" in message and "squidface" in message


@pytest.mark.parametrize("initial, expected", ((False, True), (True, False)))
async def test_cmd_cr(bot_fx, rescue_sop_fx, initial: bool, expected: bool):
    await bot_fx.board.append(rescue_sop_fx)
    async with bot_fx.board.modify_rescue(rescue_sop_fx) as case:
        case: Rescue
        case.code_red = initial

    ctx = await Context.from_message(
        bot_fx, "#unkn0wndev", "some_ov", f"!cr {rescue_sop_fx.board_index}"
    )

    await trigger(ctx)

    assert rescue_sop_fx.code_red is expected, "failed to set CR to expected value"


async def test_grab_no_recent(bot_fx, rat_board_fx):
    target = "target_user"
    # ensure the user doesn't appear to have spoken recently
    if target in bot_fx.last_user_message:
        del bot_fx.last_user_message[target]

    starting_rescue_len = len(bot_fx.board)

    ctx = await Context.from_message(bot_fx, "#ratchat", "some_ov", f"!grab {target}")
    await trigger(ctx)
    assert len(bot_fx.board) == starting_rescue_len, "case was unexpectedly created."
    message = bot_fx.sent_messages.pop()["message"].casefold()

    assert "cannot comply" in message, "emitted message did not contain a soft error"


@pytest.mark.parametrize("method", ("client", "board_index"))
async def test_grab_recent(bot_fx, rescue_sop_fx, random_string_fx, method):
    await bot_fx.board.append(rescue_sop_fx)
    bot_fx.last_user_message[rescue_sop_fx.client.casefold()] = random_string_fx
    starting_rescue_len = len(bot_fx.board)
    ctx = await Context.from_message(
        bot_fx, "#ratchat", "some_ov", f"!grab {getattr(rescue_sop_fx, method)}"
    )
    await trigger(ctx)
    assert len(bot_fx.board) == starting_rescue_len, "case was unexpectedly created."
    assert bot_fx.board[rescue_sop_fx.api_id].quotes[-1].message == random_string_fx


async def test_grab_create(bot_fx, random_string_fx):
    client = "BruhChild"
    bot_fx.last_user_message[client.casefold()] = random_string_fx
    starting_rescue_len = len(bot_fx.board)

    ctx = await Context.from_message(bot_fx, "#ratchat", "some_ov", f"!grab {client}")
    await trigger(ctx)

    assert len(bot_fx.board) == starting_rescue_len + 1, "case was unexpectedly NOT created."

    rescue = bot_fx.board[client]
    assert rescue is not None, "rescue failed to be created"
    assert rescue.client == client, "client field on rescue failed to be set"


@pytest.mark.parametrize("platform_str", ("pc", "xb", "ps"))
async def test_platform(bot_fx, rescue_sop_fx, platform_str):
    await bot_fx.board.append(rescue_sop_fx)
    ctx = await Context.from_message(
        bot_fx, "#ratchat", "some_ov", f"!{platform_str} {rescue_sop_fx.client}"
    )
    await trigger(ctx)

    assert rescue_sop_fx.platform is getattr(
        Platforms, platform_str.upper()
    ), "failed to update system"
