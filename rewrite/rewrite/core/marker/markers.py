from dataclasses import dataclass
from typing import List, Protocol, ClassVar
from uuid import UUID

from rewrite.core import random_id


class Marker(Protocol):
    id: UUID


@dataclass
class Markers:
    id: UUID
    markers: List[Marker]

    EMPTY: ClassVar = None


# noinspection PyFinal
Markers.EMPTY = Markers(random_id(), [])
