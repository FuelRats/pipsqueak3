"""
galaxy_fx.py - Testing fixtures for the Galaxy module.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.
"""

import pytest
from pytest_httpserver import HTTPServer

from src.packages.galaxy import Galaxy


@pytest.fixture(scope="session")
def mock_system_api_server_fx():
    """
    Returns a mock HTTP server with pre-built data resembling the Fuel Rats Systems API.
    """
    # pylint: disable=line-too-long

    with HTTPServer('127.0.0.1', '4000') as httpserver:
        # System Data
        # - Fuelum
        httpserver.expect_request("/api/systems/10283432").respond_with_data(
            """{"data": {"id": "10283432", "type": "systems", "attributes": {"id64": 5031721931482, "name": "Fuelum", "coords": {"x": 52.0, "y": -52.65625, "z": 49.8125}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/10283432"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/10283432"}, "meta": {}}"""
        )
        # - Beagle Point
        httpserver.expect_request("/api/systems/10369161").respond_with_data(
            """{"data": {"id": "10369161", "type": "systems", "attributes": {"id64": 81973396946, "name": "Beagle Point", "coords": {"x": -1111.5625, "y": -134.21875, "z": 65269.75}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/10369161"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/10369161"}, "meta": {}}"""
        )
        # - Eorld Pri QI-Z d1-4302
        httpserver.expect_request("/api/systems/18082834").respond_with_data(
            """{"data": {"id": "18082834", "type": "systems", "attributes": {"id64": 147826004709651, "name": "Eorld Pri QI-Z d1-4302", "coords": {"x": -320.0, "y": -49.46875, "z": 19636.6875}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/18082834"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/18082834"}, "meta": {}}"""
        )
        # - Prae Flyi RO-I b29-113
        httpserver.expect_request("/api/systems/22311274").respond_with_data(
            """{"data": {"id": "22311274", "type": "systems", "attributes": {"id64": 249152528933625, "name": "Prae Flyi RO-I b29-113", "coords": {"x": -586.125, "y": -112.0625, "z": 39248.5}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/22311274"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/22311274"}, "meta": {}}"""
        )
        # - Chua Eohn CT-F d12-2
        httpserver.expect_request("/api/systems/19626238").respond_with_data(
            """{"data": {"id": "19626238", "type": "systems", "attributes": {"id64": 78995497067, "name": "Chua Eohn CT-F d12-2", "coords": {"x": -995.5, "y": -162.59375, "z": 58857.0}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/19626238"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/19626238"}, "meta": {}}"""
        )
        # - ANGRBONII
        httpserver.expect_request("/api/systems/10288293").respond_with_data(
            """{"data": {"id": "10288293", "type": "systems", "attributes": {"id64": 40557912804216, "name": "Angrbonii", "coords": {"x": 61.65625, "y": -42.4375, "z": 53.59375}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/10288293"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/10288293"}, "meta": {}}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/api/systems").respond_with_data(
            """{"data":[],"included":[],"meta":{"results":{"available":0}}}"""
        )

        # Star Data
        # - Fuelum
        httpserver.expect_request("/api/stars", query_string=b"filter%5BsystemId:eq%5D=1464").respond_with_data(
            """{"data":[{"id":"3202571","attributes":{"id64":72062625759859420,"name":"NN 4230 B","subType":"M (Red dwarf) Star","isMainStar":false}},{"id":"3206960","attributes":{"id64":36033828740895450,"name":"Fuelum","subType":"K (Yellow-Orange) Star","isMainStar":true}}],"meta":{"results":{"available":1}}}"""
        )
        # - Angrbonii
        httpserver.expect_request("/api/stars", query_string=b"filter%5BsystemId:eq%5D=10288293").respond_with_data(
            """{"data":[{"id":"377822","attributes":{"id64":72098151950732160,"name":"Angrbonii A","subType":"L (Brown dwarf) Star","isMainStar":true}}],"meta":{"results":{"available":1}}}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/api/stars").respond_with_data(
            """{"data":[],"included":[],"meta":{"results":{"available":0}}}"""
        )

        # System Searches
        # - Fuelum
        httpserver.expect_request("/search", query_string=b"name=Fuelum&limit=1").respond_with_data(
            """{"meta":{"name":"Fuelum","type":"Perfect match"},"data":[{"name":"Fuelum","similarity":"Perfect match","id":10283432}]}"""
        )
        # - Angrbonii
        httpserver.expect_request("/search", query_string=b"name=Angrbonii&limit=1").respond_with_data(
            """{"meta":{"name":"Angrbonii","type":"Perfect match"},"data":[{"name":"Angrbonii","similarity":"Perfect match","id":10288293}]}"""
        )
        # - Beagle Point
        httpserver.expect_request("/search", query_string=b"name=Beagle+Point&limit=1").respond_with_data(
            """{"meta":{"name":"Beagle Point","type":"Perfect match"},"data":[{"name":"Beagle Point","similarity":"Perfect match","id":10369161}]}"""
        )
        # - Eorld Pri QI-Z d1-4302
        httpserver.expect_request("/search", query_string=b"name=Eorld+Pri+QI-Z+d1-4302&limit=1").respond_with_data(
            """{"meta":{"name":"Eorld Pri QI-Z d1-4302","type":"Perfect match"},"data":[{"name":"Eorld Pri QI-Z d1-4302","similarity":"Perfect match","id":18082834}]}"""
        )
        # - Prae Flyi RO-I b29-113
        httpserver.expect_request("/search", query_string=b"name=Prae+Flyi+RO-I+b29-113&limit=1").respond_with_data(
            """{"meta": {"name": "Prae Flyi RO-I b29-113", "type": "Perfect match"}, "data": [{"name": "Prae Flyi RO-I b29-113", "similarity": "Perfect match","id":22311274}]}"""
        )
        # - Chua Eohn CT-F d12-2
        httpserver.expect_request("/search", query_string=b"name=Chua+Eohn+CT-F+d12-2&limit=1").respond_with_data(
            """{"meta": {"name": "Chua Eohn CT-F d12-2", "type": "Perfect match"}, "data": [{"name": "Chua Eohn CT-F d12-2", "similarity": "Perfect match", "id": 19626238}]}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/search").respond_with_data(
            """{"meta":{"name":"","type":"dmeta"},"data":[{"name":"h","similarity":0,"id":11633548}]}"""
        )

        # Fuzzy Searches
        # - Fualun
        httpserver.expect_request("/mecha", query_string=b"name=FUALUN").respond_with_data(
            """{"meta":{"name":"FUALUN"},"data":[{"name":"Walun","similarity":0.3}]}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/mecha").respond_with_data(
            """{"meta":{"name":"","error":"No hits."}}"""
        )

        # Nearest Star Systems
        # - Fuelum to Beagle Point Waypoint 1
        httpserver.expect_request("/nearest", query_string=b"x=-297.61975614106245&y=-77.16362400032693&z=19646.678714135756&aggressive=1&limit=10&cubesize=50").respond_with_data(
            """{"data":[{"name":"Eorld Pri QI-Z d1-4302"}]}"""
        )
        # - Fuelum to Beagle Point Waypoint 2
        httpserver.expect_request("/nearest", query_string=b"x=-659.9347713269128&y=-85.86445074372631&z=39233.70563297652&aggressive=1&limit=10&cubesize=50").respond_with_data(
            """{"data":[{"name":"Prae Flyi RO-I b29-113"}]}"""
        )
        # - Fuelum to Beagle Point Waypoint 3
        httpserver.expect_request("/nearest", query_string=b"x=-981.8197621017766&y=-128.7478566272249&z=58844.498245920506&aggressive=1&limit=10&cubesize=50").respond_with_data(
            """{"data":[{"name":"Chua Eohn CT-F d12-2"}]}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/nearest").respond_with_data(
            """{"data":[]}"""
        )

        # Tests that Galaxy will retry failed requests
        httpserver.expect_oneshot_request("/badendpoint").respond_with_data(status = 400)
        httpserver.expect_oneshot_request("/badendpoint").respond_with_data(status = 500)
        httpserver.expect_oneshot_request("/badendpoint").respond_with_data("""{"success":true}""")
        httpserver.expect_request("/reallybadendpoint").respond_with_data(status = 404)

        yield httpserver


@pytest.fixture(scope="session")
def galaxy_fx(mock_system_api_server_fx) -> Galaxy: # pylint: disable=redefined-outer-name
    """
    Test fixture for Galaxy. Includes a mock API server with pre-made calls.
    """

    return Galaxy(mock_system_api_server_fx.url_for("/"))
