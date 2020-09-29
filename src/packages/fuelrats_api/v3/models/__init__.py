import cattr
from uuid import UUID
cattr.register_structure_hook(UUID, lambda data, _: UUID(data))
