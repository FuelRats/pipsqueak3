import json
from importlib import resources
from uuid import UUID

import pytest

from src.packages.fuelrats_api.v3.models.v1.nickname import Nickname
from .. import v3_tests
import cattr

pytestmark = [pytest.mark.unit, pytest.mark.api_v3]


def test_parse():
    # The linter incorrectly flags __init__.py as not a module type
    # noinspection PyTypeChecker
    assert resources.is_resource(v3_tests, "raw_nickname_response.json")
    # The linter incorrectly flags __init__.py as not a module type
    # noinspection PyTypeChecker
    raw = resources.read_text(v3_tests, "raw_nickname_response.json")
    payload = json.loads(raw)

    nickname = cattr.structure(payload['data'][0], Nickname)
    assert nickname.id == UUID('00000000-0000-4000-0000-000000000048')
    assert nickname.attributes.vhost == "clapton.recruit.fuelrats.com"
    assert nickname.attributes.nick == "ClappersClappyton"
    assert nickname.relationships.rat.links
