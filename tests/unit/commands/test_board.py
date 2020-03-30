from uuid import uuid4

import pytest

from src.packages.context import Context
from src.commands import case_management
from src.packages.rat import Rat
from src.packages.rescue import Rescue
from src.packages.utils import Platforms

pytestmark = [pytest.mark.unit, pytest.mark.commands, pytest.mark.asyncio]


@pytest.mark.parametrize("initial, expected", [(False, True), (True, False)])
async def test_active(rat_board_fx, bot_fx, initial: bool, expected: bool):
    case = await bot_fx.board.create_rescue(client="snafu", active=initial)
    ctx = await Context.from_message(
        bot_fx, "#unkn0wndev", "some_ov", f"!active {case.board_index}"
    )

    await case_management.cmd_case_management_active(ctx)

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
    await case_management.cmd_case_management_assign(ctx)
    for name in names:
        assert (
            name in rescue_sop_fx.unidentified_rats
        ), "failed to assign unidentified rats"

    # verify unassign behavior while we are here (less duplication than a distinct test)
    ctx = await Context.from_message(
        bot=bot_fx,
        channel="#unkn0wndev",
        sender="some_ov",
        message=f"!unassign {rescue_sop_fx.board_index} {' '.join(names)}",
    )
    await case_management.cmd_case_management_unassign(ctx)
    for name in names:
        assert (
            name not in rescue_sop_fx.unidentified_rats
        ), "failed to unassign unidentified rats"


async def test_clear_no_rat(rescue_sop_fx, bot_fx):
    await bot_fx.board.append(rescue_sop_fx)
    ctx = await Context.from_message(
        bot_fx, "#unkn0wndev", "some_ov", f"!clear {rescue_sop_fx.board_index}"
    )
    await case_management.cmd_case_management_clear(ctx)
    assert rescue_sop_fx.board_index not in bot_fx.board, "failed to clear rescue"


async def test_clear_invalid(bot_fx):
    rescue = await bot_fx.board.create_rescue(
        uuid=uuid4(),
        client="no_cheese_no_life",
        active=True,
        system=None,
        platform=None,
    )
    ctx = await Context.from_message(
        bot_fx, "#unkn0wndev", "some_ov", f"!clear {rescue.board_index}"
    )
    await case_management.cmd_case_management_clear(ctx)

    # neither rescue nor platform are set
    assert rescue.board_index in bot_fx.board, "unexpectedly cleared rescue"
    assert bot_fx.sent_messages, "bot failed to reply to user"
    message = bot_fx.sent_messages.pop()["message"].casefold()
    assert "cannot comply" in message, "failed to give correct error message"
    async with bot_fx.board.modify_rescue(rescue) as case:
        case: Rescue
        case.system = "Ki"

    # platform not set

    await case_management.cmd_case_management_clear(ctx)
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
        bot_fx,
        "#unkn0wndev",
        "some_ov",
        f"!clear {rescue.board_index} jack_the_ripper[pc]",
    )

    await case_management.cmd_case_management_clear(ctx)
    assert rescue.board_index in bot_fx.board, "unexpectedly cleared rescue"
    message = bot_fx.sent_messages.pop()["message"].casefold()
    assert "cannot comply" in message, "failed to bail out"
    assert "unidentified" in message, "failed to give correct error message"
