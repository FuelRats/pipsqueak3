"""
api_manager_fx.py - Testing fixtures for the API Manager module.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.
"""

import pytest
from pytest_httpserver import HTTPServer

from src.packages.api import APIManager


@pytest.fixture(scope="session")
def mock_api_server_fx():
    """
    Returns a mock HTTP server with pre-built data resembling the Fuel Rats API.
    """
    # pylint: disable=line-too-long

    with HTTPServer('127.0.0.1', '4001') as httpserver:
        ### Rat Data ###
        # - rat1
        httpserver.expect_request("/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d").respond_with_data(
            """
{"data": {"id": "8dfb8593-4694-44f2-af2f-686b1e6cf48d", "type": "rats", "attributes": {"name": "rat1", "data": null, "platform": "pc", "createdAt": "2019-07-11T09:14:48.441770+02:00", "updatedAt": "2019-07-11T09:14:48.441884+02:00"}, "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d"}, "related": {}, "relationships": {"user": {"data": null, "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d/relationships/user", "related": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d/user"}, "meta": {"direction": "MANYTOONE", "results": {}}}}, "meta": {"forbidden_fields": []}}, "included": [], "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d"}, "meta": {}}"""
        )

        ### Rat Searches ###
        # - name: rat1
        httpserver.expect_request("/rats", query_string=b"filter%5Bname:ilike%5D=rat1").respond_with_data(
            """{"data": [{"id": "8dfb8593-4694-44f2-af2f-686b1e6cf48d", "type": "rats", "attributes": {"name": "rat1", "data": null, "platform": "pc", "createdAt": "2019-07-11T09:14:48.441770+02:00", "updatedAt": "2019-07-11T09:14:48.441884+02:00"}, "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d"}, "related": {}, "relationships": {"user": {"data": null, "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d/relationships/user", "related": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d/user"}, "meta": {"direction": "MANYTOONE", "results": {}}}}, "meta": {"forbidden_fields": []}}], "included": [], "links": {"first": "http://127.0.0.1/api/rats?sort=id&filter%5Bname%3Ailike%5D=rat1&page%5Boffset%5D=0", "last": "http://127.0.0.1/api/rats?sort=id&filter%5Bname%3Ailike%5D=rat1&page%5Boffset%5D=0", "self": "http://127.0.0.1/api/rats?filter[name:ilike]=rat1"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )

        # - name: rat1
        # - platform: pc
        httpserver.expect_request("/rats", query_string=b"filter%5Bname:ilike%5D=rat1&filter%5Bplatform:eq%5D=pc").respond_with_data(
            """{"data": [{"id": "8dfb8593-4694-44f2-af2f-686b1e6cf48d", "type": "rats", "attributes": {"name": "rat1", "data": null, "platform": "pc", "createdAt": "2019-07-11T09:14:48.441770+02:00", "updatedAt": "2019-07-11T09:14:48.441884+02:00"}, "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d"}, "related": {}, "relationships": {"user": {"data": null, "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d/relationships/user", "related": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d/user"}, "meta": {"direction": "MANYTOONE", "results": {}}}}, "meta": {"forbidden_fields": []}}], "included": [], "links": {"first": "http://127.0.0.1/api/rats?sort=id&filter%5Bname%3Ailike%5D=rat1&filter%5Bplatform%3Aeq%5D=pc&page%5Boffset%5D=0", "last": "http://127.0.0.1/api/rats?sort=id&filter%5Bname%3Ailike%5D=rat1&filter%5Bplatform%3Aeq%5D=pc&page%5Boffset%5D=0", "self": "http://127.0.0.1/api/rats?filter[name:ilike]=rat1&filter[platform:eq]=pc"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )

        ### Rescue Data ###
        # Open rescue with rat1 assigned
        httpserver.expect_request("/rescues/26560069-ff2f-485d-bd11-8cb878b570c0", query_string=b"include=rats").respond_with_data(
            """{"data": {"id": "26560069-ff2f-485d-bd11-8cb878b570c0", "type": "rescues", "attributes": {"client": "pcClient", "codeRed": false, "data": {"langID": "en", "status": {}, "IRCNick": "pcClient", "boardIndex": 24, "markedForDeletion": {"marked": false, "reason": null, "reporter": null}}, "notes": null, "platform": "pc", "quotes": [], "status": "open", "system": "FIRESTONE", "title": null, "outcome": null, "unidentifiedRats": [], "createdAt": "2019-07-11T09:15:07.431666+02:00", "updatedAt": "2019-07-11T09:15:07.431724+02:00"}, "links": {"self": "http://127.0.0.1/api/rescues/26560069-ff2f-485d-bd11-8cb878b570c0"}, "related": {}, "relationships": {"firstLimpet": {"data": null, "links": {"self": "http://127.0.0.1/api/rescues/26560069-ff2f-485d-bd11-8cb878b570c0/relationships/firstLimpet", "related": "http://127.0.0.1/api/rescues/26560069-ff2f-485d-bd11-8cb878b570c0/firstLimpet"}, "meta": {"direction": "MANYTOONE", "results": {}}}, "rats": {"data": [{"type": "rats", "id": "8dfb8593-4694-44f2-af2f-686b1e6cf48d"}], "links": {"self": "http://127.0.0.1/api/rescues/26560069-ff2f-485d-bd11-8cb878b570c0/relationships/rats", "related": "http://127.0.0.1/api/rescues/26560069-ff2f-485d-bd11-8cb878b570c0/rats"}, "meta": {"direction": "MANYTOMANY", "results": {"limit": 10, "available": 1, "returned": 1}}}}, "meta": {"forbidden_fields": []}}, "included": [{"id": "8dfb8593-4694-44f2-af2f-686b1e6cf48d", "type": "rats", "attributes": {"name": "rat1", "data": null, "platform": "pc", "createdAt": "2019-07-11T09:14:48.441770+02:00", "updatedAt": "2019-07-11T09:14:48.441884+02:00"}, "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d"}, "related": {}, "relationships": {"user": {"data": null, "links": {"self": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d/relationships/user", "related": "http://127.0.0.1/api/rats/8dfb8593-4694-44f2-af2f-686b1e6cf48d/user"}, "meta": {"direction": "MANYTOONE", "results": {}}}}, "meta": {"forbidden_fields": []}}], "links": {"self": "http://127.0.0.1/api/rescues/26560069-ff2f-485d-bd11-8cb878b570c0?include=rats"}, "meta": {}}"""
        )

        # 404 response for id "random-uuid"
        httpserver.expect_request("/rescues/random-uuid", query_string=b"include=rats").respond_with_data(
            """{"errors": [{"code": "404", "detail": "Object random-uuid not found in collection rescues", "title": "Not Found"}]}""",
            status=404
        )

        yield httpserver


@pytest.fixture(scope='session')
def api_manager_fx(mock_api_server_fx) -> APIManager:  # pylint: disable=redefined-outer-name
    """
    Test fixture for APIManager. Includes a mock API server with pre-made calls.
    """
    base_url = mock_api_server_fx.url_for('/')
    config = {'api': {'url': base_url, 'online_mode': True}}
    return APIManager(config)