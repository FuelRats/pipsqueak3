import pytest

from src.packages.utils import Status, Platforms

pytestmark = [pytest.mark.fuelrats_api, pytest.mark.asyncio, pytest.mark.integration]


async def test_create_rescue(board_online_fx, rescue_plain_fx):
    """ verifies a case can be created via the online board"""
    # return Rescue(uuid4(), "UNIT_TEST", "ki", "UNIT_TEST", board_index=42, status=Status.OPEN,
    #               platform=Platforms.PC)

    rescue = await  board_online_fx.create_rescue(
        "UNIT_TEST", "ki", "UNIT_TEST", status=Status.OPEN, platform=Platforms.PC
    )
    ...

    rescue_plain_fx._api_id = rescue.api_id
    rescue_plain_fx.board_index = rescue.board_index

    assert rescue_plain_fx == rescue
