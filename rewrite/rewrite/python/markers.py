from __future__ import annotations

from dataclasses import dataclass, replace
from uuid import UUID

from rewrite import Marker


@dataclass(frozen=True, eq=False)
class KeywordArguments(Marker):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id_: UUID) -> 'KeywordArguments':
        return self if id_ is self._id else replace(self, _id=id_)


@dataclass(frozen=True, eq=False)
class KeywordOnlyArguments(Marker):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id_: UUID) -> 'KeywordOnlyArguments':
        return self if id_ is self._id else replace(self, _id=id_)
