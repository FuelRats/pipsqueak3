import json
import uuid
from typing import Dict, Any, List
from uuid import UUID

import cattr

from ..converters import to_uuid

from loguru import logger
import attr


@attr.dataclass
class Request:
    endpoint: List[str] = attr.ib(
        validator=attr.validators.deep_iterable(
            member_validator=attr.validators.instance_of(str),
            iterable_validator=attr.validators.instance_of(list),
        )
    )
    """
    An array pointing to a specific resource you would like to make a request to,
     this is basically the Websocket API equivalent to a URL, and the WebSocket endpoint equivalent
    to each endpoint is specified in that endpoint's documentation.
    """
    query: Dict[str, Any] = attr.ib(validator=attr.validators.instance_of(dict), factory=dict)
    """
    Request query information object, corresponding to the url query parameters you would send
     in an HTTP request.
    """
    body: Dict[Any, Any] = attr.ib(validator=attr.validators.instance_of(dict), factory=dict)
    """
    The body data of the message, corresponding to the information you would have in the body of an
     HTTP request.
    """

    state: str = attr.ib(factory=uuid.uuid4, validator=attr.validators.instance_of(UUID))
    """
    The state parameter can be any random string, it is used as a unique identifier that will be
     sent back in replies allowing you to identify what request a response is in reply to.
    """

    def serialize(self) -> str:
        """ serializes this request into the form the websocket expects"""
        frame = [self.state, self.endpoint, self.query, self.body]
        return json.dumps(cattr.unstructure(frame))


@attr.dataclass
class Response:
    state: UUID = attr.ib(validator=attr.validators.instance_of(UUID), converter=to_uuid)
    status: int = attr.ib(validator=attr.validators.instance_of(int))
    body: dict = attr.ib(validator=attr.validators.instance_of(dict))

    @classmethod
    def deserialize(cls, raw: str) -> "Response":
        """
        Deserializes the provided `raw` into a Response object

        Args:
            raw: message to decode

        Returns:
            Response object
        """
        state, status, body, *erroneous = json.loads(raw)
        if erroneous:
            logger.error("Failed to parse API response!")
        return cls(state=state, status=status, body=body)
