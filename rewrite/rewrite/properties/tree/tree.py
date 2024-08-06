from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Protocol, Optional
from uuid import UUID
from enum import Enum

from ...core import Tree, SourceFile
from ...core.marker.markers import Markers


class Properties(Tree, Protocol):
    pass


class Content(Properties, Protocol):
    pass


@dataclass(eq=False, frozen=True)
class File(Properties, SourceFile):
    id: UUID
    prefix: str
    markers: Markers
    source_path: str

    def with_id(self, value: UUID) -> File:
        return self if self.id == value else replace(self, id=value)

    def with_prefix(self, value: str) -> File:
        return self if self.prefix == value else replace(self, prefix=value)

    def with_markers(self, value: Markers) -> File:
        return self if self.markers == value else replace(self, markers=value)

    def with_source_path(self, value: str) -> File:
        return self if self.source_path == value else replace(self, source_path=value)


@dataclass(eq=False, frozen=True)
class Entry(Content):
    id: UUID
    prefix: str
    markers: Markers
    key: str
    before_equals: str
    delimiter: Optional[Delimiter]
    value: Value

    class Delimiter(Enum):
        COLON = ':'
        EQUALS = '='
        NONE = '\0'


@dataclass(eq=False, frozen=True)
class Value:
    id: UUID
    prefix: str
    markers: Markers
    text: str


@dataclass(eq=False, frozen=True)
class Comment:
    id: UUID
    prefix: str
    markers: Markers
    delimiter: Delimiter
    message: str

    class Delimiter(Enum):
        HASH_TAG = '#'
        EXCLAMATION_MARK = '!'
