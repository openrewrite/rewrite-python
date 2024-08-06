from __future__ import annotations

import weakref
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol
from uuid import UUID
from enum import Enum

from .additional_types import *
from ...core import Checksum, FileAttributes, SourceFile, Tree
from ...core.marker.markers import Markers

class Json(Tree, Protocol):
    pass

@dataclass(frozen=True, eq=False)
class Array(JsonValue):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Array:
        return self if id is self._id else Array(self._id, self._prefix, self._markers, self._values)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Array:
        return self if prefix is self._prefix else Array(self._id, self._prefix, self._markers, self._values)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Array:
        return self if markers is self._markers else Array(self._id, self._prefix, self._markers, self._values)

    _values: List[JsonRightPadded[JsonValue]]

    @property
    def values(self) -> List[JsonValue]:
        return JsonRightPadded.get_elements(self._values)

    def with_values(self, values: List[JsonValue]) -> Array:
        return self.padding.with_values(JsonRightPadded.with_elements(self._values, values))

    @dataclass
    class PaddingHelper:
        _t: Array

        @property
        def values(self) -> List[JsonRightPadded[JsonValue]]:
            return self._t._values

        def with_values(self, values: List[JsonRightPadded[JsonValue]]) -> Array:
            return self._t if self._t._values is values else Array(self._t.id, self._t.prefix, self._t.markers, values)

    _padding: weakref.ReferenceType[Array.PaddingHelper] = None

    @property
    def padding(self) -> Array.PaddingHelper:
        p: Array.PaddingHelper
        if self._padding is None:
            p = Array.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Array.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class Document(Json, SourceFile["Document"]):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Document:
        return self if id is self._id else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _source_path: Path

    @property
    def source_path(self) -> Path:
        return self._source_path

    def with_source_path(self, source_path: Path) -> Document:
        return self if source_path is self._source_path else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Document:
        return self if prefix is self._prefix else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Document:
        return self if markers is self._markers else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _charset_name: Optional[str]

    @property
    def charset_name(self) -> Optional[str]:
        return self._charset_name

    def with_charset_name(self, charset_name: Optional[str]) -> Document:
        return self if charset_name is self._charset_name else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _charset_bom_marked: bool

    @property
    def charset_bom_marked(self) -> bool:
        return self._charset_bom_marked

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> Document:
        return self if charset_bom_marked is self._charset_bom_marked else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _checksum: Optional[Checksum]

    @property
    def checksum(self) -> Optional[Checksum]:
        return self._checksum

    def with_checksum(self, checksum: Optional[Checksum]) -> Document:
        return self if checksum is self._checksum else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _file_attributes: Optional[FileAttributes]

    @property
    def file_attributes(self) -> Optional[FileAttributes]:
        return self._file_attributes

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> Document:
        return self if file_attributes is self._file_attributes else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _value: JsonValue

    @property
    def value(self) -> JsonValue:
        return self._value

    def with_value(self, value: JsonValue) -> Document:
        return self if value is self._value else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

    _eof: Space

    @property
    def eof(self) -> Space:
        return self._eof

    def with_eof(self, eof: Space) -> Document:
        return self if eof is self._eof else Document(self._id, self._source_path, self._prefix, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._value, self._eof)

@dataclass(frozen=True, eq=False)
class Empty(JsonValue):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Empty:
        return self if id is self._id else Empty(self._id, self._prefix, self._markers)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Empty:
        return self if prefix is self._prefix else Empty(self._id, self._prefix, self._markers)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Empty:
        return self if markers is self._markers else Empty(self._id, self._prefix, self._markers)

@dataclass(frozen=True, eq=False)
class Identifier(JsonKey):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Identifier:
        return self if id is self._id else Identifier(self._id, self._prefix, self._markers, self._name)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Identifier:
        return self if prefix is self._prefix else Identifier(self._id, self._prefix, self._markers, self._name)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Identifier:
        return self if markers is self._markers else Identifier(self._id, self._prefix, self._markers, self._name)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> Identifier:
        return self if name is self._name else Identifier(self._id, self._prefix, self._markers, self._name)

@dataclass(frozen=True, eq=False)
class Literal(JsonValue, JsonKey):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Literal:
        return self if id is self._id else Literal(self._id, self._prefix, self._markers, self._source, self._value)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Literal:
        return self if prefix is self._prefix else Literal(self._id, self._prefix, self._markers, self._source, self._value)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Literal:
        return self if markers is self._markers else Literal(self._id, self._prefix, self._markers, self._source, self._value)

    _source: str

    @property
    def source(self) -> str:
        return self._source

    def with_source(self, source: str) -> Literal:
        return self if source is self._source else Literal(self._id, self._prefix, self._markers, self._source, self._value)

    _value: object

    @property
    def value(self) -> object:
        return self._value

    def with_value(self, value: object) -> Literal:
        return self if value is self._value else Literal(self._id, self._prefix, self._markers, self._source, self._value)

@dataclass(frozen=True, eq=False)
class Member(Json):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Member:
        return self if id is self._id else Member(self._id, self._prefix, self._markers, self._key, self._value)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Member:
        return self if prefix is self._prefix else Member(self._id, self._prefix, self._markers, self._key, self._value)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Member:
        return self if markers is self._markers else Member(self._id, self._prefix, self._markers, self._key, self._value)

    _key: JsonRightPadded[JsonKey]

    @property
    def key(self) -> JsonKey:
        return self._key.element

    def with_key(self, key: JsonKey) -> Member:
        return self.padding.with_key(JsonRightPadded.with_element(self._key, key))

    _value: JsonValue

    @property
    def value(self) -> JsonValue:
        return self._value

    def with_value(self, value: JsonValue) -> Member:
        return self if value is self._value else Member(self._id, self._prefix, self._markers, self._key, self._value)

    @dataclass
    class PaddingHelper:
        _t: Member

        @property
        def key(self) -> JsonRightPadded[JsonKey]:
            return self._t._key

        def with_key(self, key: JsonRightPadded[JsonKey]) -> Member:
            return self._t if self._t._key is key else Member(self._t.id, self._t.prefix, self._t.markers, key, self._t.value)

    _padding: weakref.ReferenceType[Member.PaddingHelper] = None

    @property
    def padding(self) -> Member.PaddingHelper:
        p: Member.PaddingHelper
        if self._padding is None:
            p = Member.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = Member.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

@dataclass(frozen=True, eq=False)
class JsonObject(JsonValue):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> JsonObject:
        return self if id is self._id else JsonObject(self._id, self._prefix, self._markers, self._members)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> JsonObject:
        return self if prefix is self._prefix else JsonObject(self._id, self._prefix, self._markers, self._members)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JsonObject:
        return self if markers is self._markers else JsonObject(self._id, self._prefix, self._markers, self._members)

    _members: List[JsonRightPadded[Json]]

    @property
    def members(self) -> List[Json]:
        return JsonRightPadded.get_elements(self._members)

    def with_members(self, members: List[Json]) -> JsonObject:
        return self.padding.with_members(JsonRightPadded.with_elements(self._members, members))

    @dataclass
    class PaddingHelper:
        _t: JsonObject

        @property
        def members(self) -> List[JsonRightPadded[Json]]:
            return self._t._members

        def with_members(self, members: List[JsonRightPadded[Json]]) -> JsonObject:
            return self._t if self._t._members is members else JsonObject(self._t.id, self._t.prefix, self._t.markers, members)

    _padding: weakref.ReferenceType[JsonObject.PaddingHelper] = None

    @property
    def padding(self) -> JsonObject.PaddingHelper:
        p: JsonObject.PaddingHelper
        if self._padding is None:
            p = JsonObject.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            if p is None or p._t != self:
                p = JsonObject.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p
