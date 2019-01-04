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
        httpserver.expect_request("/systems", query_string=b"filter%5Bname:like%5D=FUELUM&include=bodies&").respond_with_data(
            """{"data":[{"id":"4878","attributes":{"name":"FUELUM","x":52,"y":-52.65625,"z":49.8125,"is_populated":1}}],"included":[{"id":"3274797","attributes":{"name":"Fuelum","spectral_class":"K"}}],"meta":{"results":{"available":1}}}"""
        )
        # - Beagle Point
        httpserver.expect_request("/systems", query_string=b"filter%5Bname:like%5D=BEAGLE+POINT&include=bodies&").respond_with_data(
            """{"data":[{"id":"47005","attributes":{"name":"BEAGLE POINT","x":-1111.5625,"y":-134.21875,"z":65269.75,"is_populated":0}}],"included":[{"id":"9319","attributes":{"name":"Beagle Point","spectral_class":"K"}}],"meta":{"results":{"available":1}}}"""
        )
        # - EORLD PRI QI-Z D1-4302
        httpserver.expect_request("/systems", query_string=b"filter%5Bname:like%5D=EORLD+PRI+QI-Z+D1-4302&include=bodies&").respond_with_data(
            """{"data":[{"id":"7366711","attributes":{"name":"EORLD PRI QI-Z D1-4302","x":-320,"y":-49.46875,"z":19636.6875,"is_populated":0}}],"included":[],"meta":{"results":{"available":1}}}"""
        )
        # - PRAE FLYI RO-I B29-113
        httpserver.expect_request("/systems", query_string=b"filter%5Bname:like%5D=PRAE+FLYI+RO-I+B29-113&include=bodies&").respond_with_data(
            """{"data":[{"id":"11782614","attributes":{"name":"PRAE FLYI RO-I B29-113","x":-586.125,"y":-112.0625,"z":39248.5,"is_populated":0}}],"included":[],"meta":{"results":{"available":1}}}"""
        )
        # - CHUA EOHN CT-F D12-2
        httpserver.expect_request("/systems", query_string=b"filter%5Bname:like%5D=CHUA+EOHN+CT-F+D12-2&include=bodies&").respond_with_data(
            """{"data":[{"id":"11814429","attributes":{"name":"CHUA EOHN CT-F D12-2","x":-995.5,"y":-162.59375,"z":58857,"is_populated":0}}],"included":[],"meta":{"results":{"available":1}}}"""
        )
        # - ANGRBONII
        httpserver.expect_request("/systems", query_string=b"filter%5Bname:like%5D=ANGRBONII&include=bodies&").respond_with_data(
            """{"data":[{"id":"987","attributes":{"name":"ANGRBONII","x":61.65625,"y":-42.4375,"z":53.59375,"is_populated":1}}],"included":[{"id":"31601","attributes":{"name":"Angrbonii A","spectral_class":"L"}}],"meta":{"results":{"available":1}}}"""
        )
        # - CRUCIS SECTOR EW-N A6-0
        httpserver.expect_request("/systems", query_string=b"filter%5Bname:like%5D=CRUCIS+SECTOR+EW-N+A6-0&include=bodies&").respond_with_data(
            """{"data":[{"id":"42919","attributes":{"name":"CRUCIS SECTOR EW-N A6-0","x":55.65625,"y":-35.9375,"z":49.71875,"is_populated":0}}],"included":[{"id":"31601","attributes":{"name":"Crucis Sector EW-N a6-0","spectral_class":"M"}}],"meta":{"results":{"available":1}}}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/systems").respond_with_data(
            """{"data":[],"included":[],"meta":{"results":{"available":0}}}"""
        )

        # Fuzzy Searches
        # - Fualun
        httpserver.expect_request("/search", query_string=b"name=FUALUN&type=soundex&limit=5&").respond_with_data(
            """{"data":[{"name":"FUELUM"},{"name":"FOLNA"},{"name":"FEI LIN"}]}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/search").respond_with_data(
            """{"data":[]}"""
        )

        # Nearest Star Systems
        # - Fuelum to Beagle Point Waypoint 1
        httpserver.expect_request("/nearest", query_string=b"x=-297.61975614106245&y=-77.16362400032693&z=19646.678714135756&aggressive=1&limit=10&").respond_with_data(
            """{"data":[{"name":"EORLD PRI QI-Z D1-4302"}]}"""
        )
        # - Fuelum to Beagle Point Waypoint 2
        httpserver.expect_request("/nearest", query_string=b"x=-659.9347713269128&y=-85.86445074372631&z=39233.70563297652&aggressive=1&limit=10&").respond_with_data(
            """{"data":[{"name":"PRAE FLYI RO-I B29-113"}]}"""
        )
        # - Fuelum to Beagle Point Waypoint 3
        httpserver.expect_request("/nearest", query_string=b"x=-981.8197621017766&y=-128.7478566272249&z=58844.498245920506&aggressive=1&limit=10&").respond_with_data(
            """{"data":[{"name":"CHUA EOHN CT-F D12-2"}]}"""
        )
        # - Angrbonii Scoopable Search
        httpserver.expect_request("/nearest", query_string=b"x=61.65625&y=-42.4375&z=53.59375&aggressive=1&limit=50&include=1&").respond_with_data(
            """{"candidates":[{"name":"ANGRBONII"},{"name":"ELLRI"},{"name":"FINTI"},{"name":"CRUCIS SECTOR EW-N A6-0"}],"included":{"bodies":[{"name":"Angrbonii A","spectral_class":"L"},{"name":"Finti","spectral_class":"L"},{"name":"Crucis Sector EW-N a6-0","spectral_class":"M"}]}}"""
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
