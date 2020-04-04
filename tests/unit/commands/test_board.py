from uuid import uuid4

import hypothesis
import pytest
from hypothesis import strategies

from src.packages.commands.rat_command import trigger
from src.packages.context import Context
from src.packages.rat import Rat
from src.packages.rescue import Rescue
from src.packages.utils import Platforms, sanitize
from tests import strategies as custom_strategies

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
    message = bot_fx.sent_messages.pop(0)["message"].casefold()
    assert "cannot comply" in message, "failed to give correct error message"
    async with bot_fx.board.modify_rescue(rescue) as case:
        case: Rescue
        case.system = "Ki"

    # platform not set

    await trigger(ctx)
    assert rescue.board_index in bot_fx.board, "unexpectedly cleared rescue"
    message = bot_fx.sent_messages.pop(0)["message"].casefold()
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
    message = bot_fx.sent_messages.pop(0)["message"].casefold()
    assert "cannot comply" in message, "failed to bail out"
    assert "unidentified" in message, "failed to give correct error message"


async def test_cmd_cmdr(bot_fx, rescue_sop_fx):
    await bot_fx.board.append(rescue_sop_fx)
    ctx = await Context.from_message(
        bot_fx, "#unkn0wndev", "some_ov", f"!cmdr {rescue_sop_fx.board_index} squidface"
    )

    await trigger(ctx)
    assert rescue_sop_fx.client == "squidface", "failed to assign commander"
    message = bot_fx.sent_messages.pop(0)["message"].casefold()
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
    message = bot_fx.sent_messages.pop(0)["message"].casefold()

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


@pytest.mark.parametrize("cr_state", (True, False))
async def test_quote(bot_fx, rescue_sop_fx, cr_state: bool):
    rescue_sop_fx.code_red = cr_state
    await bot_fx.board.append(rescue_sop_fx)

    ctx = await Context.from_message(
        bot_fx, "#ratchat", "some_ov", f"!quote {rescue_sop_fx.board_index}"
    )

    await trigger(ctx)

    message = bot_fx.sent_messages.pop(0)["message"].casefold()
    _test_quote_header(cr_state, message, rescue_sop_fx)


def _test_quote_header(cr_state, message, rescue):
    assert f"{rescue.board_index}" in message, "case number missing"
    assert rescue.client.casefold() in message, "client name missing"
    assert rescue.platform.value.casefold() in message, "platform missing"
    assert "none" not in message, "somethings null thats not supposed to be"
    if rescue.irc_nickname == rescue.client:
        assert "irc nickname" not in message, "irc nickname incorrectly rendered"
    if cr_state:
        assert "cr" in message, "code red state missing"


@pytest.mark.parametrize("cr_state", (True, False))
@pytest.mark.parametrize("platform", (Platforms.PC, Platforms.XB, Platforms.PS))
async def test_quote_inject_interop(bot_fx, cr_state: bool, platform: Platforms):
    inject_ctx = await Context.from_message(bot_fx, "#ratchat", "some_ov",
                                            f"!inject subject PC sol {'cr' if cr_state else ''}")
    # inject a case into existance
    await trigger(inject_ctx)
    rescue = bot_fx.board["subject"]

    ctx = await Context.from_message(bot_fx, "#ratchat", "some_ov", f"!quote {rescue.board_index}")
    await trigger(ctx)
    message = bot_fx.sent_messages.pop(0)["message"].casefold()
    _test_quote_header(cr_state, message, rescue)
    if cr_state:
        message = bot_fx.sent_messages.pop(0)["message"].casefold()
        assert "code red!" in message, "cr message missing!"
    message = bot_fx.sent_messages.pop(0)["message"].casefold()
    assert f"{rescue.api_id}" in message, "rescue uuid missing"
    assert F"{rescue.board_index}" in message, "incorrect / missing board index"


@pytest.mark.hypothesis
@hypothesis.given(
    cr_state=strategies.booleans(),
    client=custom_strategies.valid_word,
    payload=custom_strategies.valid_text,
    platform=strategies.sampled_from([Platforms.PC, Platforms.XB, Platforms.PS]),
)
async def test_inject_creates_rescue(bot_fx, cr_state: bool, platform: Platforms, client: str,
                                     payload: str):
    hypothesis.assume(client not in bot_fx.board)  # new rescue
    starting_rescue_count = len(bot_fx.board)
    await bot_fx.on_message("#ratchat", "some_ov",
                            f"!inject {client} {platform.value} {'cr' if cr_state else ''} {payload}",
                            )
    message = ""
    while "case opened" not in message and bot_fx.sent_messages:
        message = bot_fx.sent_messages.pop(0)["message"].casefold()
    assert len(bot_fx.board) == starting_rescue_count + 1
    assert "case opened" in message
    if cr_state:
        assert "cr" in message
    assert client.casefold() in message
    # cleanup steps since Hypothesis reuses fixtures
    await bot_fx.board.remove_rescue(sanitize(client))
    bot_fx.sent_messages.clear()


@pytest.mark.asyncio
async def test_sub_replace(bot_fx, rescue_sop_fx, random_string_fx):
    rescue_sop_fx.add_quote("i like pizza", "somebody")
    await bot_fx.board.append(rescue_sop_fx)
    initial_quote_count = len(rescue_sop_fx.quotes)

    context = await Context.from_message(bot_fx, "#unittest", "some_admin",
                                         f"!sub {rescue_sop_fx.irc_nickname} 0 {random_string_fx}")
    try:
        await trigger(context)
    except:
        pytest.fail("exception occured")
    assert len(rescue_sop_fx.quotes) == initial_quote_count, "quote added / deleted unexpectedly"


@pytest.mark.asyncio
async def test_sub_replace(bot_fx, rescue_sop_fx):
    rescue_sop_fx.add_quote("i like pizza", "somebody")
    await bot_fx.board.append(rescue_sop_fx)
    initial_quote_count = len(rescue_sop_fx.quotes)

    context = await Context.from_message(bot_fx, "#unittest", "some_admin",
                                         f"!sub {rescue_sop_fx.irc_nickname} 0")
    await trigger(context)
    assert len(rescue_sop_fx.quotes) == initial_quote_count - 1, "quote added / deleted unexpectedly"


@pytest.mark.asyncio
@pytest.mark.hypothesis
@hypothesis.given(
    initial_content=custom_strategies.valid_text,
    new_content=custom_strategies.valid_text,
    author=custom_strategies.valid_word,
    rescue=custom_strategies.rescues
)
async def test_sub_replace_hypothesis(bot_fx, rescue, initial_content: str, new_content: str,
                                      author: str):
    rescue.quotes.clear()
    # ensure a quote exists
    rescue.add_quote(initial_content, author)
    await bot_fx.board.append(rescue, overwrite=True)
    context = await Context.from_message(bot_fx, "#unittest", "some_admin",
                                         f"!sub {rescue.irc_nickname} 0 {new_content}")

    await trigger(context)
    assert rescue.quotes, "quote deleted!"
    assert rescue.quotes[0].message == new_content, "content changed to something unexpected"

    await bot_fx.board.remove_rescue(rescue)
