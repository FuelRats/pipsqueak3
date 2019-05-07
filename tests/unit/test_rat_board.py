"""
Unittest file for the Rat_Board module.
"""

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.ratboard]


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ("SicklyTadpole", "xxxRiderxxx", "f1sh_sticks"))
async def test_create_rescue(rat_board_fx, name):
    """ verifies a rescue can be created via Create"""
    async with rat_board_fx.create_rescue(client=name) as rescue:
        assert rescue.client == name, "client didn't match!"

    assert name in rat_board_fx, "rescue didn't make it in!"


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
