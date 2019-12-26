import json
from importlib import resources

import pytest

from src.packages.fuelrats_api.v3._converters import nickname_converter
from .. import v3_tests

pytestmark = [pytest.mark.unit, pytest.mark.api_v3]


def test_parse():
    # The linter incorrectly flags __init__.py as not a module type
    # noinspection PyTypeChecker
    assert resources.is_resource(v3_tests, "raw_nickname_response.json")
    # The linter incorrectly flags __init__.py as not a module type
    # noinspection PyTypeChecker
    raw = resources.read_text(v3_tests, "raw_nickname_response.json")
    payload = json.loads(raw)

    nickname = nickname_converter.NicknameConverter.from_api(payload['data'][0])
