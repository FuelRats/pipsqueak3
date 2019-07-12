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

    #with HTTPServer('127.0.0.1', '4001') as httpserver:


@pytest.fixture(scope='session')
def api_manager_fx(mock_api_server_fx) -> APIManager:
    config = {'api': {'url': 'https://apiv3.fuelrats.dev/api/', 'online_mode': True}}
    return APIManager(config)
