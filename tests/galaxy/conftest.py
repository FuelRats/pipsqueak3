"""
galaxy/conftest.py - Testing fixtures for the Galaxy module.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.
"""

import pytest
from pytest_httpserver import HTTPServer

from Modules.galaxy import Galaxy


@pytest.fixture(scope="session")
def mock_system_api_server_fx():
    """
    Returns a mock HTTP server with pre-built data resembling the Fuel Rats Systems API.
    """
    # pylint: disable=line-too-long

    with HTTPServer() as httpserver:
        # System Data
        # - Fuelum
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:eq%5D=FUELUM").respond_with_data(
            """{"data":[{"id":"1464","attributes":{"name":"FUELUM","id64":5031721931482,"coords":{"x":52,"y":-52.65625,"z":49.8125}}}],"meta":{"results":{"available":1}}}"""
        )
        # - Beagle Point
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:eq%5D=BEAGLE+POINT").respond_with_data(
            """{"data":[{"id":"124406","attributes":{"name":"BEAGLE POINT","id64":81973396946,"coords":{"x":-1111.5625,"y":-134.21875,"z":65269.75}}}],"meta":{"results":{"available":1}}}"""
        )
        # - EORLD PRI QI-Z D1-4302
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:eq%5D=EORLD+PRI+QI-Z+D1-4302").respond_with_data(
            """{"data":[{"id":"10189923","attributes":{"name":"EORLD PRI QI-Z D1-4302","id64":147826004709651,"coords":{"x":-320,"y":-49.46875,"z":19636.6875}}}],"meta":{"results":{"available":1}}}"""
        )
        # - PRAE FLYI RO-I B29-113
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:eq%5D=PRAE+FLYI+RO-I+B29-113").respond_with_data(
            """{"data":[{"id":"14576787","attributes":{"name":"PRAE FLYI RO-I B29-113","id64":249152528933625,"coords":{"x":-586.125,"y":-112.0625,"z":39248.5}}}],"meta":{"results":{"available":1}}}"""
        )
        # - CHUA EOHN CT-F D12-2
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:eq%5D=CHUA+EOHN+CT-F+D12-2").respond_with_data(
            """{"data":[{"id":"11814429","attributes":{"name":"CHUA EOHN CT-F D12-2","id64":78995497067,"coords":{"x":-995.5,"y":-162.59375,"z":58857}}}],"meta":{"results":{"available":1}}}"""
        )
        # - ANGRBONII
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:eq%5D=ANGRBONII").respond_with_data(
            """{"data":[{"id":"6337","attributes":{"name":"ANGRBONII","id64":40557912804216,"coords":{"x":61.65625,"y":-42.4375,"z":53.59375}}}],"meta":{"results":{"available":1}}}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/api/systems").respond_with_data(
            """{"data":[],"included":[],"meta":{"results":{"available":0}}}"""
        )

        # Star Data
        # - Fuelum
        httpserver.expect_request("/api/stars", query_string=b"filter%5BsystemId64:eq%5D=5031721931482&filter%5BisMainStar:eq%5D=1").respond_with_data(
            """{"data":[{"id":"3206960","attributes":{"id64":36033828740895450,"name":"Fuelum","subType":"K (Yellow-Orange) Star","isMainStar":true}}],"meta":{"results":{"available":1}}}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/api/stars").respond_with_data(
            """{"data":[],"included":[],"meta":{"results":{"available":0}}}"""
        )

        # Fuzzy Searches
        # - Fualun
        httpserver.expect_request("/search", query_string=b"name=FUALUN&type=dmeta&limit=5").respond_with_data(
            """{"data":[{"name":"FOLNA"},{"name":"FEI LIN"},{"name":"FEI LIAN"}]}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/search").respond_with_data(
            """{"data":[]}"""
        )

        # Nearest Star Systems
        # - Fuelum to Beagle Point Waypoint 1
        httpserver.expect_request("/nearest", query_string=b"x=-297.61975614106245&y=-77.16362400032693&z=19646.678714135756&aggressive=1&limit=10&cubesize=50").respond_with_data(
            """{"data":[{"name":"EORLD PRI QI-Z D1-4302"}]}"""
        )
        # - Fuelum to Beagle Point Waypoint 2
        httpserver.expect_request("/nearest", query_string=b"x=-659.9347713269128&y=-85.86445074372631&z=39233.70563297652&aggressive=1&limit=10&cubesize=50").respond_with_data(
            """{"data":[{"name":"PRAE FLYI RO-I B29-113"}]}"""
        )
        # - Fuelum to Beagle Point Waypoint 3
        httpserver.expect_request("/nearest", query_string=b"x=-981.8197621017766&y=-128.7478566272249&z=58844.498245920506&aggressive=1&limit=10&cubesize=50").respond_with_data(
            """{"data":[{"name":"CHUA EOHN CT-F D12-2"}]}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/nearest").respond_with_data(
            """{"data":[]}"""
        )

        yield httpserver


@pytest.fixture(scope="session")
def galaxy_fx(mock_system_api_server_fx) -> Galaxy: # pylint: disable=redefined-outer-name
    """
    Test fixture for Galaxy. Includes a mock API server with pre-made calls.
    """

    return Galaxy(mock_system_api_server_fx.url_for("/"))
