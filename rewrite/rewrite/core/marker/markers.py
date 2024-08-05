from dataclasses import dataclass
from typing import List, Protocol, ClassVar
from uuid import UUID

from rewrite.core import random_id


class Marker(Protocol):
    id: UUID

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


@dataclass(frozen=True, eq=False)
class Markers:
    id: UUID
    markers: List[Marker]

    EMPTY: ClassVar = None

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)


# noinspection PyFinal
Markers.EMPTY = Markers(random_id(), [])
