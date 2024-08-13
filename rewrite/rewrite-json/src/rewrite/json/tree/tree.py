from __future__ import annotations

import weakref
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol, runtime_checkable, TYPE_CHECKING
from uuid import UUID
from enum import Enum

if TYPE_CHECKING:
    from ..visitor import JsonVisitor
from .support_types import *
from rewrite import Checksum, FileAttributes, SourceFile, Tree, TreeVisitor
from rewrite.marker import Markers

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Array(JsonValue):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Array:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Array:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Array:
        return self if markers is self._markers else replace(self, _markers=markers)

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
            return self._t if self._t._values is values else replace(self._t, _values=values)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: Array.PaddingHelper
        if self._padding is None:
            p = Array.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = Array.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def __init__(self, id: UUID, prefix: Space, markers: Markers, values: List[JsonRightPadded[JsonValue]]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_values', values)

    def accept_json(self, v: JsonVisitor[P], p: P) -> Json:
        return v.visit_array(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Document(SourceFile):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Document:
        return self if id is self._id else replace(self, _id=id)

    _source_path: Path

    @property
    def source_path(self) -> Path:
        return self._source_path

    def with_source_path(self, source_path: Path) -> Document:
        return self if source_path is self._source_path else replace(self, _source_path=source_path)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Document:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Document:
        return self if markers is self._markers else replace(self, _markers=markers)

    _charset_name: Optional[str]

    @property
    def charset_name(self) -> Optional[str]:
        return self._charset_name

    def with_charset_name(self, charset_name: Optional[str]) -> Document:
        return self if charset_name is self._charset_name else replace(self, _charset_name=charset_name)

    _charset_bom_marked: bool

    @property
    def charset_bom_marked(self) -> bool:
        return self._charset_bom_marked

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> Document:
        return self if charset_bom_marked is self._charset_bom_marked else replace(self, _charset_bom_marked=charset_bom_marked)

    _checksum: Optional[Checksum]

    @property
    def checksum(self) -> Optional[Checksum]:
        return self._checksum

    def with_checksum(self, checksum: Optional[Checksum]) -> Document:
        return self if checksum is self._checksum else replace(self, _checksum=checksum)

    _file_attributes: Optional[FileAttributes]

    @property
    def file_attributes(self) -> Optional[FileAttributes]:
        return self._file_attributes

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> Document:
        return self if file_attributes is self._file_attributes else replace(self, _file_attributes=file_attributes)

    _value: JsonValue

    @property
    def value(self) -> JsonValue:
        return self._value

    def with_value(self, value: JsonValue) -> Document:
        return self if value is self._value else replace(self, _value=value)

    _eof: Space

    @property
    def eof(self) -> Space:
        return self._eof

    def with_eof(self, eof: Space) -> Document:
        return self if eof is self._eof else replace(self, _eof=eof)

    def __init__(self, id: UUID, source_path: Path, prefix: Space, markers: Markers, charset_name: Optional[str], charset_bom_marked: bool, checksum: Optional[Checksum], file_attributes: Optional[FileAttributes], value: JsonValue, eof: Space) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_source_path', source_path)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_charset_name', charset_name)
        object.__setattr__(self, '_charset_bom_marked', charset_bom_marked)
        object.__setattr__(self, '_checksum', checksum)
        object.__setattr__(self, '_file_attributes', file_attributes)
        object.__setattr__(self, '_value', value)
        object.__setattr__(self, '_eof', eof)

    def accept_json(self, v: JsonVisitor[P], p: P) -> Json:
        return v.visit_document(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Empty(JsonValue):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Empty:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Empty:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Empty:
        return self if markers is self._markers else replace(self, _markers=markers)

    def __init__(self, id: UUID, prefix: Space, markers: Markers) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)

    def accept_json(self, v: JsonVisitor[P], p: P) -> Json:
        return v.visit_empty(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Identifier(JsonKey):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Identifier:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Identifier:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Identifier:
        return self if markers is self._markers else replace(self, _markers=markers)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> Identifier:
        return self if name is self._name else replace(self, _name=name)

    def __init__(self, id: UUID, prefix: Space, markers: Markers, name: str) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_name', name)

    def accept_json(self, v: JsonVisitor[P], p: P) -> Json:
        return v.visit_identifier(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Literal(JsonValue, JsonKey):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Literal:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Literal:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Literal:
        return self if markers is self._markers else replace(self, _markers=markers)

    _source: str

    @property
    def source(self) -> str:
        return self._source

    def with_source(self, source: str) -> Literal:
        return self if source is self._source else replace(self, _source=source)

    _value: object

    @property
    def value(self) -> object:
        return self._value

    def with_value(self, value: object) -> Literal:
        return self if value is self._value else replace(self, _value=value)

    def __init__(self, id: UUID, prefix: Space, markers: Markers, source: str, value: object) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_source', source)
        object.__setattr__(self, '_value', value)

    def accept_json(self, v: JsonVisitor[P], p: P) -> Json:
        return v.visit_literal(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Member(Json):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Member:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> Member:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Member:
        return self if markers is self._markers else replace(self, _markers=markers)

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
        return self if value is self._value else replace(self, _value=value)

    @dataclass
    class PaddingHelper:
        _t: Member

        @property
        def key(self) -> JsonRightPadded[JsonKey]:
            return self._t._key

        def with_key(self, key: JsonRightPadded[JsonKey]) -> Member:
            return self._t if self._t._key is key else replace(self._t, _key=key)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: Member.PaddingHelper
        if self._padding is None:
            p = Member.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = Member.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def __init__(self, id: UUID, prefix: Space, markers: Markers, key: JsonRightPadded[JsonKey], value: JsonValue) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_key', key)
        object.__setattr__(self, '_value', value)

    def accept_json(self, v: JsonVisitor[P], p: P) -> Json:
        return v.visit_member(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class JsonObject(JsonValue):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> JsonObject:
        return self if id is self._id else replace(self, _id=id)

    _prefix: Space

    @property
    def prefix(self) -> Space:
        return self._prefix

    def with_prefix(self, prefix: Space) -> JsonObject:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JsonObject:
        return self if markers is self._markers else replace(self, _markers=markers)

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
            return self._t if self._t._members is members else replace(self._t, _members=members)

    _padding: weakref.ReferenceType[PaddingHelper] = None

    @property
    def padding(self) -> PaddingHelper:
        p: JsonObject.PaddingHelper
        if self._padding is None:
            p = JsonObject.PaddingHelper(self)
            object.__setattr__(self, '_padding', weakref.ref(p))
        else:
            p = self._padding()
            # noinspection PyProtectedMember
            if p is None or p._t != self:
                p = JsonObject.PaddingHelper(self)
                object.__setattr__(self, '_padding', weakref.ref(p))
        return p

    def __init__(self, id: UUID, prefix: Space, markers: Markers, members: List[JsonRightPadded[Json]]) -> None:
        # generated due to https://youtrack.jetbrains.com/issue/PY-62622
        object.__setattr__(self, '_id', id)
        object.__setattr__(self, '_prefix', prefix)
        object.__setattr__(self, '_markers', markers)
        object.__setattr__(self, '_members', members)

    def accept_json(self, v: JsonVisitor[P], p: P) -> Json:
        return v.visit_object(self, p)
