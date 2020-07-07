import json
from importlib import resources
from typing import Dict
from uuid import UUID

import pytest

from src.packages.fuelrats_api.v3.models.v1.rescue import Rescue as ApiRescue
from .. import v3_tests

pytestmark = [pytest.mark.unit, pytest.mark.api_v3]

RAW_ENUMERATE_RESCUE_RESPONSE: Dict = json.loads(
    resources.read_text(v3_tests, "raw_rescue_enumerate_response.json"))


def test_deserialize():
    original = RAW_ENUMERATE_RESCUE_RESPONSE.copy()
    rescue = ApiRescue.from_dict(RAW_ENUMERATE_RESCUE_RESPONSE['data'][0])

    assert RAW_ENUMERATE_RESCUE_RESPONSE == original, "illegal mutation of input data"
    assert rescue.id == UUID("a8acc8d6-af38-4256-9911-7455e33012f2")
    assert rescue.attributes.client == "Test Client"
    assert rescue.attributes.clientLanguage is None
    assert rescue.attributes.codeRed is True
    assert rescue.attributes.commandIdentifier is None
    assert rescue.attributes.notes == 'hello world2222222!'


def test_from_internal(rescue_sop_fx):
    # assert we can build a API rescue from mecha's internal data model
    rescue = ApiRescue.from_internal(rescue_sop_fx)

    assert rescue.id == rescue_sop_fx.api_id
    assert rescue.attributes.client == rescue_sop_fx.client
    assert rescue.attributes.createdAt.tzinfo is not None