from uuid import UUID

import pytest

from src.packages.fuelrats_api.v3.mockup import MockupAPI
from src.packages.rescue import Rescue

pytestmark = [pytest.mark.fuelrats_api, pytest.mark.asyncio, pytest.mark.integration]


@pytest.fixture
def mock_fuelrats_api_fx():
    # TODO pull from configuration system
    return MockupAPI(url=r'http://api.thehellisthis.com:6543/api')


async def test_get_rescue(mock_fuelrats_api_fx, ):
    target = UUID("c1ff8456-5c51-47b1-8d0e-be6104840820")
    result = await mock_fuelrats_api_fx.get_rescue(target)

    assert isinstance(result, Rescue)


async def test_update_rescue(mock_fuelrats_api_fx, rescue_sop_fx):
    target = UUID("c1ff8456-5c51-47b1-8d0e-be6104840820")
    rescue_sop_fx._api_id = target

    await mock_fuelrats_api_fx.update_rescue(rescue_sop_fx)


async def test_create_rescue(mock_fuelrats_api_fx, rescue_plain_fx):
    result = await mock_fuelrats_api_fx.create_rescue(rescue_plain_fx)

    rescue_plain_fx._api_id = rescue_plain_fx.api_id

    assert result == rescue_plain_fx
