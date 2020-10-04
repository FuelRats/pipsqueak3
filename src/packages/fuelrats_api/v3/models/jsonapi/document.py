from typing import Optional, List, Dict, TypeVar, Generic, Any

import attr
from .jsonapi_meta import JsonApi, JsonApiMeta
from .link import Links


@attr.dataclass
class Document:
    jsonapi: JsonApi
    meta: JsonApiMeta
    data: Any
    included: List[Links]
    links: Optional[Links]

