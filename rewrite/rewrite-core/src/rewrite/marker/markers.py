from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol, ClassVar, cast, runtime_checkable
from uuid import UUID

from ..utils import random_id


@runtime_checkable
class Marker(Protocol):
    @property
    def id(self) -> UUID:
        ...

    def with_id(self, id: UUID) -> Marker:
        ...

    def __eq__(self, other: object) -> bool:
        if self.__class__ == other.__class__:
            return self.id == cast(Marker, other).id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(frozen=True, eq=False)
class Markers:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Markers:
        return self if id is self._id else Markers(id, self._markers)

    _markers: List[Marker]

    @property
    def markers(self) -> List[Marker]:
        return self._markers

    def with_markers(self, markers: List[Marker]) -> Markers:
        return self if markers is self._markers else Markers(self._id, markers)

    EMPTY: ClassVar[Markers]

    def __eq__(self, other: object) -> bool:
        if self.__class__ == other.__class__:
            return self.id == cast(Markers, other).id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


Markers.EMPTY = Markers(random_id(), [])
