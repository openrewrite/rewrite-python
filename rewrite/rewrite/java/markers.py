from dataclasses import dataclass, replace
from uuid import UUID

from rewrite import Marker


@dataclass(frozen=True, eq=False)
class Semicolon(Marker):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id_: UUID) -> Marker:
        return self if id_ is self._id else replace(self, _id=id_)
