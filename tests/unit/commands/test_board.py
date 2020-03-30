import pytest

from src.packages.context import Context
from src.commands import case_management

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
    ctx = await Context.from_message(bot=bot_fx, channel="#unkn0wndev", sender="some_ov",
                                     message=f"!assign {rescue_sop_fx.board_index} {' '.join(names)}")
    await case_management.cmd_case_management_assign(ctx)
    for name in names:
        assert name in rescue_sop_fx.unidentified_rats, "failed to assign unidentified rats"

    # verify unassign behavior while we are here (less duplication than a distinct test)
    ctx = await Context.from_message(bot=bot_fx, channel="#unkn0wndev", sender="some_ov",
                                     message=f"!unassign {rescue_sop_fx.board_index} {' '.join(names)}")
    await case_management.cmd_case_management_unassign(ctx)
    for name in names:
        assert name not in rescue_sop_fx.unidentified_rats, "failed to unassign unidentified rats"
