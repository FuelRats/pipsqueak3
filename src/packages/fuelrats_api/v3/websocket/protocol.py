from __future__ import annotations
import json
import uuid
from typing import Dict, Any, List

import attr
import asyncio


def state_factory() -> str:
    """ small factory to generate uuid4s as strings to stuff into a query state object """
    return f"{uuid.uuid4()}"


@attr.dataclass
class Request:
    endpoint: List[str] = attr.ib(validator=attr.validators.deep_iterable(
        member_validator=attr.validators.instance_of(str),
        iterable_validator=attr.validators.instance_of(list)
    ))
    """
    An array pointing to a specific resource you would like to make a request to, 
    this is basically the Websocket API equivalent to a URL, and the WebSocket endpoint equivalent
    to each endpoint is specified in that endpoint's documentation.
    """
    query: Dict[str, Any] = attr.ib(validator=attr.validators.instance_of(dict))
    """
    Request query information object, corresponding to the url query parameters you would send 
    in an HTTP request.
    """
    body: Dict[Any, Any] = attr.ib(validator=attr.validators.instance_of(dict), factory=dict)
    """
    The body data of the message, corresponding to the information you would have in the body of an 
    HTTP request.
    """

    state: str = attr.ib(factory=state_factory)
    """
    The state parameter can be any random string, it is used as a unique identifier that will be 
    sent back in replies allowing you to identify what request a response is in reply to.
    """

    def serialize(self) -> str:
        """ serializes this request into the form the websocket expects"""

        frame = [self.state, self.endpoint, self.query, self.body]
        return json.dumps(frame)


@attr.dataclass
class Response:
    state: str = attr.ib(validator=attr.validators.instance_of(str))
    status: int = attr.ib(validator=attr.validators.instance_of(int))
    body: dict = attr.ib(validator=attr.validators.instance_of(dict))

    @classmethod
    def deserialize(cls, raw: str) -> Response:
        """
        Deserializes the provided `raw` into a Response object

        Args:
            raw: message to decode

        Returns:
            Response object
        """
        return cls(*json.loads(raw))
