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
        httpserver.expect_request("/api/systems/5031721931482").respond_with_data(
            """{"data": {"id": "10283432", "type": "systems", "attributes": {"id64": 5031721931482, "name": "Fuelum", "coords": {"x": 52.0, "y": -52.65625, "z": 49.8125}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/10283432"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/10283432"}, "meta": {}}"""
        )
        # - Beagle Point
        httpserver.expect_request("/api/systems/81973396946").respond_with_data(
            """{"data": {"id": "10369161", "type": "systems", "attributes": {"id64": 81973396946, "name": "Beagle Point", "coords": {"x": -1111.5625, "y": -134.21875, "z": 65269.75}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/10369161"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/10369161"}, "meta": {}}"""
        )
        # - Eorld Pri QI-Z d1-4302
        httpserver.expect_request("/api/systems/147826004709651").respond_with_data(
            """{"data": {"id": "18082834", "type": "systems", "attributes": {"id64": 147826004709651, "name": "Eorld Pri QI-Z d1-4302", "coords": {"x": -320.0, "y": -49.46875, "z": 19636.6875}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/18082834"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/18082834"}, "meta": {}}"""
        )
        # - Prae Flyi RO-I b29-113
        httpserver.expect_request("/api/systems/249152528933625").respond_with_data(
            """{"data": {"id": "22311274", "type": "systems", "attributes": {"id64": 249152528933625, "name": "Prae Flyi RO-I b29-113", "coords": {"x": -586.125, "y": -112.0625, "z": 39248.5}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/22311274"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/22311274"}, "meta": {}}"""
        )
        # - Chua Eohn CT-F d12-2
        httpserver.expect_request("/api/systems/78995497067").respond_with_data(
            """{"data": {"id": "19626238", "type": "systems", "attributes": {"id64": 78995497067, "name": "Chua Eohn CT-F d12-2", "coords": {"x": -995.5, "y": -162.59375, "z": 58857.0}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/19626238"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/19626238"}, "meta": {}}"""
        )
        # - ANGRBONII
        httpserver.expect_request("/api/systems/40557912804216").respond_with_data(
            """{"data": {"id": "10288293", "type": "systems", "attributes": {"id64": 40557912804216, "name": "Angrbonii", "coords": {"x": 61.65625, "y": -42.4375, "z": 53.59375}}, "links": {"self": "https://system.api.fuelrats.com/api/systems/10288293"}, "related": {}, "relationships": {}, "meta": {}}, "included": [], "links": {"self": "https://system.api.fuelrats.com/api/systems/10288293"}, "meta": {}}"""
        )

        # Star Data
        # - Fuelum
        httpserver.expect_request("/api/stars", query_string=b"filter%5BsystemId64:eq%5D=5031721931482").respond_with_data(
            """{"data":[{"id":"3202571","attributes":{"id64":72062625759859420,"name":"NN 4230 B","subType":"M (Red dwarf) Star","isMainStar":false}},{"id":"3206960","attributes":{"id64":36033828740895450,"name":"Fuelum","subType":"K (Yellow-Orange) Star","isMainStar":true}}],"meta":{"results":{"available":1}}}"""
        )
        # - Angrbonii
        httpserver.expect_request("/api/stars", query_string=b"filter%5BsystemId64:eq%5D=40557912804216").respond_with_data(
            """{"data":[{"id":"377822","attributes":{"id64":72098151950732160,"name":"Angrbonii A","subType":"L (Brown dwarf) Star","isMainStar":true}}],"meta":{"results":{"available":1}}}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/api/stars").respond_with_data(
            """{"data":[],"included":[],"meta":{"results":{"available":0}}}"""
        )

        # System Searches
        # - Fuelum
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:ilike%5D=Fuelum&sort=name&limit=1").respond_with_data(
            """{"data": [{"id": "5031721931482", "type": "systems", "attributes": {"name": "Fuelum", "coords": {"x": 52.0, "y": -52.65625, "z": 49.8125}}, "links": {"self": "http://sapi.fuelrats.dev/api/systems/5031721931482"}, "related": {}, "relationships": {"planets": {"data": [{"type": "bodies", "id": "684552175082246874"}, {"type": "bodies", "id": "828667363158102746"}, {"type": "bodies", "id": "504408189987427034"}, {"type": "bodies", "id": "720580972101210842"}, {"type": "bodies", "id": "540436987006391002"}, {"type": "bodies", "id": "360293001911571162"}, {"type": "bodies", "id": "468379392968463066"}, {"type": "bodies", "id": "756609769120174810"}, {"type": "bodies", "id": "576465784025354970"}, {"type": "bodies", "id": "792638566139138778"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/5031721931482/relationships/planets", "related": "http://sapi.fuelrats.dev/api/systems/5031721931482/planets"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 10, "returned": 10}}}, "stars": {"data": [{"type": "stars", "id": "72062625759859418"}, {"type": "stars", "id": "36033828740895450"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/5031721931482/relationships/stars", "related": "http://sapi.fuelrats.dev/api/systems/5031721931482/stars"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 2, "returned": 2}}}}, "meta": {}}], "included": [], "links": {"first": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=fuelum&page%5Boffset%5D=0", "last": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=fuelum&page%5Boffset%5D=0", "self": "http://sapi.fuelrats.dev/api/systems?filter[name:ilike]=fuelum&sort=name&limit=1"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )
        # - Angrbonii
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:ilike%5D=Angrbonii&sort=name&limit=1").respond_with_data(
            """{"data": [{"id": "40557912804216", "type": "systems", "attributes": {"name": "Angrbonii", "coords": {"x": 61.65625, "y": -42.4375, "z": 53.59375}}, "links": {"self": "http://sapi.fuelrats.dev/api/systems/40557912804216"}, "related": {}, "relationships": {"planets": {"data": [{"type": "bodies", "id": "1116933265500687224"}, {"type": "bodies", "id": "720616498292083576"}, {"type": "bodies", "id": "828702889348975480"}, {"type": "bodies", "id": "792674092330011512"}, {"type": "bodies", "id": "972818077424831352"}, {"type": "bodies", "id": "936789280405867384"}, {"type": "bodies", "id": "1044875671462759288"}, {"type": "bodies", "id": "1261048453576543096"}, {"type": "bodies", "id": "1225019656557579128"}, {"type": "bodies", "id": "1297077250595507064"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/40557912804216/relationships/planets", "related": "http://sapi.fuelrats.dev/api/systems/40557912804216/planets"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 10, "returned": 10}}}, "stars": {"data": [{"type": "stars", "id": "72098151950732152"}, {"type": "stars", "id": "144155745988660088"}, {"type": "stars", "id": "108126948969696120"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/40557912804216/relationships/stars", "related": "http://sapi.fuelrats.dev/api/systems/40557912804216/stars"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 3, "returned": 3}}}}, "meta": {}}], "included": [], "links": {"first": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Angrbonii&page%5Boffset%5D=0", "last": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Angrbonii&page%5Boffset%5D=0", "self": "http://sapi.fuelrats.dev/api/systems?filter[name:ilike]=Angrbonii&sort=name&limit=1"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )
        # - Beagle Point
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:ilike%5D=Beagle+Point&sort=name&limit=1").respond_with_data(
            """{"data": [{"id": "81973396946", "type": "systems", "attributes": {"name": "Beagle Point", "coords": {"x": -1111.5625, "y": -134.21875, "z": 65269.75}}, "links": {"self": "http://sapi.fuelrats.dev/api/systems/81973396946"}, "related": {}, "relationships": {"planets": {"data": [{"type": "bodies", "id": "252201661106144722"}, {"type": "bodies", "id": "360288052163036626"}, {"type": "bodies", "id": "324259255144072658"}, {"type": "bodies", "id": "216172864087180754"}, {"type": "bodies", "id": "180144067068216786"}, {"type": "bodies", "id": "396316849182000594"}, {"type": "bodies", "id": "108086473030288850"}, {"type": "bodies", "id": "36028878992360914"}, {"type": "bodies", "id": "72057676011324882"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/81973396946/relationships/planets", "related": "http://sapi.fuelrats.dev/api/systems/81973396946/planets"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 9, "returned": 9}}}, "stars": {"data": [{"type": "stars", "id": "81973396946"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/81973396946/relationships/stars", "related": "http://sapi.fuelrats.dev/api/systems/81973396946/stars"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 1, "returned": 1}}}}, "meta": {}}], "included": [], "links": {"first": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Beagle+Point&page%5Boffset%5D=0", "last": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Beagle+Point&page%5Boffset%5D=0", "self": "http://sapi.fuelrats.dev/api/systems?filter[name:ilike]=Beagle+Point&sort=name&limit=1"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )
        # - Eorld Pri QI-Z d1-4302
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:ilike%5D=Eorld+Pri+QI-Z+d1-4302&sort=name&limit=1").respond_with_data(
            """{"data": [{"id": "147826004709651", "type": "systems", "attributes": {"name": "Eorld Pri QI-Z d1-4302", "coords": {"x": -320.0, "y": -49.46875, "z": 19636.6875}}, "links": {"self": "http://sapi.fuelrats.dev/api/systems/147826004709651"}, "related": {}, "relationships": {"planets": {"data": [], "links": {"self": "http://sapi.fuelrats.dev/api/systems/147826004709651/relationships/planets", "related": "http://sapi.fuelrats.dev/api/systems/147826004709651/planets"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 0, "returned": 0}}}, "stars": {"data": [], "links": {"self": "http://sapi.fuelrats.dev/api/systems/147826004709651/relationships/stars", "related": "http://sapi.fuelrats.dev/api/systems/147826004709651/stars"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 0, "returned": 0}}}}, "meta": {}}], "included": [], "links": {"first": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Eorld+Pri+QI-Z+d1-4302&page%5Boffset%5D=0", "last": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Eorld+Pri+QI-Z+d1-4302&page%5Boffset%5D=0", "self": "http://sapi.fuelrats.dev/api/systems?filter[name:ilike]=Eorld+Pri+QI-Z+d1-4302&sort=name&limit=1"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )
        # - Prae Flyi RO-I b29-113
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:ilike%5D=Prae+Flyi+RO-I+b29-113&sort=name&limit=1").respond_with_data(
            """{"data": [{"id": "249152528933625", "type": "systems", "attributes": {"name": "Prae Flyi RO-I b29-113", "coords": {"x": -586.125, "y": -112.0625, "z": 39248.5}}, "links": {"self": "http://sapi.fuelrats.dev/api/systems/249152528933625"}, "related": {}, "relationships": {"planets": {"data": [], "links": {"self": "http://sapi.fuelrats.dev/api/systems/249152528933625/relationships/planets", "related": "http://sapi.fuelrats.dev/api/systems/249152528933625/planets"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 0, "returned": 0}}}, "stars": {"data": [], "links": {"self": "http://sapi.fuelrats.dev/api/systems/249152528933625/relationships/stars", "related": "http://sapi.fuelrats.dev/api/systems/249152528933625/stars"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 0, "returned": 0}}}}, "meta": {}}], "included": [], "links": {"first": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Prae+Flyi+RO-I+b29-113&page%5Boffset%5D=0", "last": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Prae+Flyi+RO-I+b29-113&page%5Boffset%5D=0", "self": "http://sapi.fuelrats.dev/api/systems?filter[name:ilike]=Prae+Flyi+RO-I+b29-113&sort=name&limit=1"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )
        # - Chua Eohn CT-F d12-2
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:ilike%5D=Chua+Eohn+CT-F+d12-2&sort=name&limit=1").respond_with_data(
            """{"data": [{"id": "78995497067", "type": "systems", "attributes": {"name": "Chua Eohn CT-F d12-2", "coords": {"x": -995.5, "y": -162.59375, "z": 58857.0}}, "links": {"self": "http://sapi.fuelrats.dev/api/systems/78995497067"}, "related": {}, "relationships": {"planets": {"data": [{"type": "bodies", "id": "288230455147208811"}, {"type": "bodies", "id": "324259252166172779"}, {"type": "bodies", "id": "360288049185136747"}, {"type": "bodies", "id": "180144064090316907"}, {"type": "bodies", "id": "252201658128244843"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/78995497067/relationships/planets", "related": "http://sapi.fuelrats.dev/api/systems/78995497067/planets"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 5, "returned": 5}}}, "stars": {"data": [{"type": "stars", "id": "144115267071352939"}, {"type": "stars", "id": "72057673033425003"}, {"type": "stars", "id": "108086470052388971"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/78995497067/relationships/stars", "related": "http://sapi.fuelrats.dev/api/systems/78995497067/stars"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 3, "returned": 3}}}}, "meta": {}}], "included": [], "links": {"first": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Chua+Eohn+CT-F+d12-2&page%5Boffset%5D=0", "last": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=Chua+Eohn+CT-F+d12-2&page%5Boffset%5D=0", "self": "http://sapi.fuelrats.dev/api/systems?filter[name:ilike]=Chua+Eohn+CT-F+d12-2&sort=name&limit=1"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )
        # - LHS 3447
        httpserver.expect_request("/api/systems", query_string=b"filter%5Bname:ilike%5D=LHS+3447&sort=name&limit=1").respond_with_data(
            """{"data": [{"id": "5306465653474", "type": "systems", "attributes": {"name": "LHS 3447", "coords": {"x": -43.1875, "y": -5.28125, "z": 56.15625}}, "links": {"self": "http://sapi.fuelrats.dev/api/systems/5306465653474"}, "related": {}, "relationships": {"planets": {"data": [{"type": "bodies", "id": "900725231939752674"}, {"type": "bodies", "id": "1477185984243176162"}, {"type": "bodies", "id": "1585272375300068066"}, {"type": "bodies", "id": "1513214781262140130"}, {"type": "bodies", "id": "468379667712185058"}, {"type": "bodies", "id": "612494855788040930"}, {"type": "bodies", "id": "1765416360394887906"}, {"type": "bodies", "id": "432350870693221090"}, {"type": "bodies", "id": "396322073674257122"}, {"type": "bodies", "id": "1729387563375923938"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/5306465653474/relationships/planets", "related": "http://sapi.fuelrats.dev/api/systems/5306465653474/planets"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 10, "returned": 10}}}, "stars": {"data": [{"type": "stars", "id": "36034103484617442"}, {"type": "stars", "id": "72062900503581410"}], "links": {"self": "http://sapi.fuelrats.dev/api/systems/5306465653474/relationships/stars", "related": "http://sapi.fuelrats.dev/api/systems/5306465653474/stars"}, "meta": {"direction": "ONETOMANY", "results": {"limit": 10, "available": 2, "returned": 2}}}}, "meta": {}}], "included": [], "links": {"first": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=lhs+3447&page%5Boffset%5D=0", "last": "http://sapi.fuelrats.dev/api/systems?sort=name&filter%5Bname%3Ailike%5D=lhs+3447&page%5Boffset%5D=0", "self": "http://sapi.fuelrats.dev/api/systems?filter%5Bname:ilike%5D=lhs+3447&sort=name&limit=1"}, "meta": {"results": {"available": 1, "limit": 10, "offset": 0, "returned": 1}}}"""
        )
        # - Fallthrough for failed searches
        httpserver.expect_request("/api/systems").respond_with_data(
            """{"data":[],"included":[],"meta":{"results":{"available":0}}}"""
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

        # Landmark searches
        # - Angrbonii
        httpserver.expect_request("/landmark", query_string=b"name=Angrbonii").respond_with_data(
            """{"meta": {"name": "Angrbonii"}, "landmarks": [{"name": "Fuelum", "distance": 14.5622606203501}]}"""
        )
        # - Fuelum
        httpserver.expect_request("/landmark", query_string=b"name=Fuelum").respond_with_data(
            """{"meta": {"name": "Fuelum"}, "landmarks": [{"name": "Fuelum", "distance": 0.00450693909432589}]}"""
        )
        # - LHS 3447
        httpserver.expect_request("/landmark", query_string=b"name=LHS+3447").respond_with_data(
            """{"meta": {"name": "LHS 3447"}, "landmarks": [{"name": "Sol", "distance": 71.0392579625871}]}"""
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
