"""
Unittest file for the Rat_Board module.
"""
import itertools
from contextlib import suppress

import pytest

from src.packages.board.board import CYCLE_AT

pytestmark = [pytest.mark.unit, pytest.mark.ratboard]


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ("SicklyTadpole", "xxxRiderxxx", "f1sh_sticks"))
async def test_create_rescue(rat_board_fx, name):
    """ verifies a rescue can be created via Create"""
    async with rat_board_fx.create_rescue(client=name) as rescue:
        assert rescue.client == name, "client didn't match!"

    assert name in rat_board_fx, "rescue didn't make it in!"
    assert rescue.board_index == 0, "board gave us the wrong index"


@pytest.mark.asyncio
async def test_append_rescue(rescue_sop_fx, rat_board_fx):
    """
    Verify rescue, when appended, is contained within the Ratboard object.
    """
    await rat_board_fx.append(rescue_sop_fx)
    assert rescue_sop_fx.api_id in rat_board_fx._storage_by_uuid


@pytest.mark.asyncio
async def test_iter(rescue_plain_fx, rescue_sop_fx, rat_board_fx):
    # append some rescues to the board object
    await rat_board_fx.append(rescue_sop_fx)
    await rat_board_fx.append(rescue_plain_fx)

    uuids = [uuid for uuid in rat_board_fx]

    assert rescue_plain_fx.api_id in uuids, "plain rescue not found in iterator!"
    assert rescue_sop_fx.api_id in uuids, "SOP rescue not found in iterator!"


@pytest.mark.asyncio
async def test_len(rescue_sop_fx, rat_board_fx):
    """ tests len(rat_board_fx)"""

    # length should be zero here
    assert len(rat_board_fx) == 0, "empty rat_board_fx somehow has a non-zero length"

    # add a rescue
    await rat_board_fx.append(rescue_sop_fx)

    # assert the length changed as expected
    assert len(rat_board_fx) == 1, "length of rat_board_fx should be exactly one here"


@pytest.mark.asyncio
async def test_getitem(rat_board_fx, rescues_fx):
    """ tests that `__getitem__` works properly"""
    await rat_board_fx.append(rescues_fx)

    assert rat_board_fx[
               rescues_fx.board_index] is rescues_fx, "getattr did not return the expected rescue object"

    assert rat_board_fx[
               rescues_fx.api_id] is rescues_fx, "getattr did not return the expected rescue object"
    assert rat_board_fx[
               rescues_fx.client] is rescues_fx, "getattr did not return the expected rescue object"


def test_getitem_invalid(rat_board_fx):
    """ verifies that if getitem is passed an invalid key type it differs to the superclass."""

    with pytest.raises(KeyError):
        # this clearly shouldn't work, but just in case (and for coverage -_-)
        _ = rat_board_fx[(42, "I like pizza")]


@pytest.mark.asyncio
async def test_free_case_roll_over_free(rat_board_fx):
    """
    Verifies the board resets its counter, and assigns a free index on [0, CYCLE_AT]
    (as such an index should be free)
    """

    # create a rescue
    async with rat_board_fx.create_rescue() as rescue:
        ...
    # hack the counter
    rat_board_fx._index_counter = itertools.count(CYCLE_AT + 1)
    # render assertion
    assert rat_board_fx.free_case_number == 1, "board did not give us the correct board index"


@pytest.mark.asyncio
async def test_free_case_rollover_no_free(rat_board_fx, random_string_fx):
    """
    tests that the board will assign case numbers > CYCLE_AT as necessary
    """

    for index in range(CYCLE_AT + 15):
        async with rat_board_fx.create_rescue(client=random_string_fx) as rescue:
            assert rescue.board_index == index, "bad index assigned"


@pytest.mark.asyncio
async def test_modify_rescue_client(rescues_fx, rat_board_fx, random_string_fx):
    """
    Verifies the board behaves correctly when the client name is changed
    """
    old_client = rescues_fx.client
    await rat_board_fx.append(rescues_fx)

    async with rat_board_fx.modify_rescue(rescues_fx.client) as rescue:
        rescue.client = random_string_fx

    assert old_client not in rat_board_fx, "bad index still in board"
    assert random_string_fx in rat_board_fx, "new client name not in board"


@pytest.mark.asyncio
async def test_modify_rescue_explosion(rat_board_fx, random_string_fx):
    """
    verifies the board doesn't drop a case when an exception is raised inside a modify_rescue() call
    """
    async with rat_board_fx.create_rescue(client=random_string_fx):
        ...

    with suppress(RuntimeError):  # intentionally suppress the exception we raise
        async with rat_board_fx.modify_rescue(random_string_fx):
            raise RuntimeError  # intentionally raise an exception

    assert random_string_fx in rat_board_fx, "the board dropped the rescue!"
