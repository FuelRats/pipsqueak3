import json
from importlib import resources

import pytest

from src.packages.fuelrats_api.v3.models.v1.nickname import Nickname
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

    nickname = Nickname.from_dict(payload['data'][0])
    assert nickname.id == 21
    assert nickname.attributes.vhost is None
    assert nickname.attributes.nick == "unknown"
    assert nickname.relationships.rat.links
