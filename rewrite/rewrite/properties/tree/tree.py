from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from ...core import Tree
from ...core.marker.markers import Markers, Marker
from ...core.tree import SourceFile


class Properties(Tree, Protocol):
    pass


@dataclass
class File(Properties, SourceFile):
    id: UUID
    prefix: str
    markers: Markers
    sourcePath: str
