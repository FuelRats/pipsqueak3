"""
jsonapi_matcher.py - Extension to pytest-httpserver's match for JSON matching.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.
"""

import json
from pytest_httpserver.httpserver import Request, RequestMatcher


class JsonApiRequestMatcher(RequestMatcher):
    """
    Extended version of pytest-httpserver's RequestMatcher that can match
    data as JSON objects rather than simple strings.
    """
    def match_data(self, request: Request) -> bool:
        """
        Matches the data part of the request. Will parse both data strings
        into JSON format and compare their dict forms.

        Args:
            request (Request): The request to match the data against.

        Returns:
            True if the request's data matches our data, either through string
            comparison, or by parsing both data values as JSON objects and
            comparing them.
            False if data does not match, or JSON data fails to parse.
        """
        if self.data is None or super().match_data(request):
            return True

        try:
            my_data = json.loads(self.data)
            request_data = json.loads(request.data)
            if my_data == request_data:
                return True
        except json.decoder.JSONDecodeError:
            return False

        return False
