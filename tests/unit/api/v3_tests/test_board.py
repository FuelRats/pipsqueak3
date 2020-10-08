import asyncio
from uuid import UUID

import cattr
import pytest

from src.packages.fuelrats_api.v3.websocket.protocol import Response, Request
from src.packages.rescue import Rescue

pytestmark = [pytest.mark.asyncio, pytest.mark.api_v3]


def test_board_on_online(mock_fuelrats_api_fx):
    pytest.fail("fixme")


async def test_get_rescue(api_wss_fx, api_wss_connection_fx):
    target = UUID("c1ff8456-5c51-47b1-8d0e-be6104840820")
    api_wss_connection_fx.expect(request=Request(
        state=UUID("282a22b2-e44f-45e2-a711-712ebca24f64"),
        endpoint=["rescues", "search"], query={"filter": {"status": {"eq": "open"}}}, body={}
    ),
        respond_with=Response(state=UUID('282a22b2-e44f-45e2-a711-712ebca24f64'), status=200,
                              body={'jsonapi': {'version': '1.0', 'meta': {'apiVersion': '3.0.0'}},
                                    'meta': {'page': 1, 'lastPage': 1, 'offset': 0, 'limit': 100,
                                             'total': 1, 'apiVersion': '3.0.0', 'rateLimitTotal': 3600,
                                             'rateLimitRemaining': 3599,
                                             'rateLimitReset': '2020-10-05T02:00:00.000Z'}, 'links': {
                                      'self': 'https://dev.api.fuelrats.com/rescues?page%5Bsize%5D=100&page%5Bnumber%5D=1&filter=%7B%22status%22%3A%7B%22eq%22%3A%22open%22%7D%7D',
                                      'first': 'https://dev.api.fuelrats.com/rescues?page%5Bsize%5D=100&page%5Bnumber%5D=1&filter=%7B%22status%22%3A%7B%22eq%22%3A%22open%22%7D%7D',
                                      'last': 'https://dev.api.fuelrats.com/rescues?page%5Bsize%5D=100&page%5Bnumber%5D=1&filter=%7B%22status%22%3A%7B%22eq%22%3A%22open%22%7D%7D'},
                                    'data': [{'type': 'rescues',
                                              'id': '8e927cbb-a265-4663-84ce-0a7dcf74770e',
                                              'attributes': {'client': 'Privateer Sand',
                                                             'clientNick': 'Privateer_Sand',
                                                             'clientLanguage': 'en-US',
                                                             'commandIdentifier': 0, 'codeRed': False,
                                                             'data': {}, 'notes': '', 'platform': 'pc',
                                                             'system': 'QB-Z A 15-5', 'title': None,
                                                             'unidentifiedRats': [],
                                                             'createdAt': '2020-10-04T21:41:42.724Z',
                                                             'updatedAt': '2020-10-05T00:52:39.219Z',
                                                             'status': 'open', 'outcome': None,
                                                             'quotes': [
                                                                 {'author': 'unknown', 'message': '1',
                                                                  'createdAt': '2020-10-04T21:42:27.215099Z',
                                                                  'updatedAt': '2020-10-05T00:52:39.086700Z',
                                                                  'lastAuthor': 'unknown'},
                                                                 {'author': 'unknown',
                                                                  'message': 'i like pizza',
                                                                  'createdAt': '2020-10-05T00:52:29.442518Z',
                                                                  'updatedAt': '2020-10-05T00:52:29.442521Z',
                                                                  'lastAuthor': 'Mecha'}]}, 'meta': {},
                                              'relationships': {'rats': {'links': {
                                                  'self': 'https://dev.api.fuelrats.com/rescues/8e927cbb-a265-4663-84ce-0a7dcf74770e/relationships/rats',
                                                  'related': 'https://dev.api.fuelrats.com/rescues/8e927cbb-a265-4663-84ce-0a7dcf74770e/rats'},
                                                  'data': []}, 'firstLimpet': {
                                                  'links': {
                                                      'self': 'https://dev.api.fuelrats.com/rescues/8e927cbb-a265-4663-84ce-0a7dcf74770e/relationships/firstLimpet',
                                                      'related': 'https://dev.api.fuelrats.com/rescues/8e927cbb-a265-4663-84ce-0a7dcf74770e/firstLimpet'},
                                                  'data': None}, 'epics': {'links': {
                                                  'self': 'https://dev.api.fuelrats.com/rescues/8e927cbb-a265-4663-84ce-0a7dcf74770e/relationships/epics',
                                                  'related': 'https://dev.api.fuelrats.com/rescues/8e927cbb-a265-4663-84ce-0a7dcf74770e/epics'},
                                                  'data': []}}, 'links': {
                                            'self': 'https://dev.api.fuelrats.com/rescues/8e927cbb-a265-4663-84ce-0a7dcf74770e'}}],
                                    'included': []})
    )
    result = await asyncio.wait_for(api_wss_fx.get_rescues(impersonate=None),
                                    timeout=1.0)

    assert result, "bad parse"
    assert isinstance(result[0], Rescue), "invalid type"
    rescue = result[0]
    assert rescue.client == "Privateer Sand"
    assert rescue.irc_nickname == "Privateer_Sand"