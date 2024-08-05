from dataclasses import dataclass, replace
from typing import Protocol
from uuid import UUID

from ...core import Tree, SourceFile
from ...core.marker.markers import Markers, Marker


class Properties(Tree, Protocol):
    pass


@dataclass(eq=False, frozen=True)
class File(Properties, SourceFile):
    id: UUID
    prefix: str
    markers: Markers
    source_path: str

    def with_id(self, value: UUID):
        return self if self.id == value else replace(self, id=value)

    def with_prefix(self, value: str):
        return self if self.prefix == value else replace(self, prefix=value)

    def with_markers(self, value: Markers):
        return self if self.markers == value else replace(self, markers=value)

    def with_source_path(self, value: str):
        return self if self.source_path == value else replace(self, source_path=value)
