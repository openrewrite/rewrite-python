from __future__ import annotations

import extensions
import weakref
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol, runtime_checkable
from uuid import UUID
from enum import Enum

from .support_types import *
from ..visitor import YamlVisitor, P
from rewrite import Checksum, FileAttributes, SourceFile, Tree
from rewrite.marker import Markers

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Documents(Yaml, SourceFile["Documents"]):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Documents:
        return self if id is self._id else replace(self, _id=id)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Documents:
        return self if markers is self._markers else replace(self, _markers=markers)

    _source_path: Path

    @property
    def source_path(self) -> Path:
        return self._source_path

    def with_source_path(self, source_path: Path) -> Documents:
        return self if source_path is self._source_path else replace(self, _source_path=source_path)

    _file_attributes: Optional[FileAttributes]

    @property
    def file_attributes(self) -> Optional[FileAttributes]:
        return self._file_attributes

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> Documents:
        return self if file_attributes is self._file_attributes else replace(self, _file_attributes=file_attributes)

    _charset_name: Optional[str]

    @property
    def charset_name(self) -> Optional[str]:
        return self._charset_name

    def with_charset_name(self, charset_name: Optional[str]) -> Documents:
        return self if charset_name is self._charset_name else replace(self, _charset_name=charset_name)

    _charset_bom_marked: bool

    @property
    def charset_bom_marked(self) -> bool:
        return self._charset_bom_marked

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> Documents:
        return self if charset_bom_marked is self._charset_bom_marked else replace(self, _charset_bom_marked=charset_bom_marked)

    _checksum: Optional[Checksum]

    @property
    def checksum(self) -> Optional[Checksum]:
        return self._checksum

    def with_checksum(self, checksum: Optional[Checksum]) -> Documents:
        return self if checksum is self._checksum else replace(self, _checksum=checksum)

    _documents: List[Document]

    @property
    def documents(self) -> List[Document]:
        return self._documents

    def with_documents(self, documents: List[Document]) -> Documents:
        return self if documents is self._documents else replace(self, _documents=documents)

    def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
        return v.visit_documents(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Document(Yaml):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Document:
        return self if id is self._id else replace(self, _id=id)

    _prefix: str

    @property
    def prefix(self) -> str:
        return self._prefix

    def with_prefix(self, prefix: str) -> Document:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Document:
        return self if markers is self._markers else replace(self, _markers=markers)

    _explicit: bool

    @property
    def explicit(self) -> bool:
        return self._explicit

    def with_explicit(self, explicit: bool) -> Document:
        return self if explicit is self._explicit else replace(self, _explicit=explicit)

    _block: Block

    @property
    def block(self) -> Block:
        return self._block

    def with_block(self, block: Block) -> Document:
        return self if block is self._block else replace(self, _block=block)

    _end: End

    @property
    def end(self) -> End:
        return self._end

    def with_end(self, end: End) -> Document:
        return self if end is self._end else replace(self, _end=end)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class End(Yaml):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Document.End:
            return self if id is self._id else replace(self, _id=id)

        _prefix: str

        @property
        def prefix(self) -> str:
            return self._prefix

        def with_prefix(self, prefix: str) -> Document.End:
            return self if prefix is self._prefix else replace(self, _prefix=prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Document.End:
            return self if markers is self._markers else replace(self, _markers=markers)

        _explicit: bool

        @property
        def explicit(self) -> bool:
            return self._explicit

        def with_explicit(self, explicit: bool) -> Document.End:
            return self if explicit is self._explicit else replace(self, _explicit=explicit)

        def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
            return v.visit_document_end(self, p)

    def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
        return v.visit_document(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Block(Yaml):
    pass

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Scalar(Block, YamlKey):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Scalar:
        return self if id is self._id else replace(self, _id=id)

    _prefix: str

    @property
    def prefix(self) -> str:
        return self._prefix

    def with_prefix(self, prefix: str) -> Scalar:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Scalar:
        return self if markers is self._markers else replace(self, _markers=markers)

    _style: Style

    @property
    def style(self) -> Style:
        return self._style

    def with_style(self, style: Style) -> Scalar:
        return self if style is self._style else replace(self, _style=style)

    _anchor: Optional[Anchor]

    @property
    def anchor(self) -> Optional[Anchor]:
        return self._anchor

    def with_anchor(self, anchor: Optional[Anchor]) -> Scalar:
        return self if anchor is self._anchor else replace(self, _anchor=anchor)

    _value: str

    @property
    def value(self) -> str:
        return self._value

    def with_value(self, value: str) -> Scalar:
        return self if value is self._value else replace(self, _value=value)

    class Style(Enum):
        DOUBLE_QUOTED = 0
        SINGLE_QUOTED = 1
        LITERAL = 2
        FOLDED = 3
        PLAIN = 4

    def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
        return v.visit_scalar(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Mapping(Block):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Mapping:
        return self if id is self._id else replace(self, _id=id)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Mapping:
        return self if markers is self._markers else replace(self, _markers=markers)

    _opening_brace_prefix: Optional[str]

    @property
    def opening_brace_prefix(self) -> Optional[str]:
        return self._opening_brace_prefix

    def with_opening_brace_prefix(self, opening_brace_prefix: Optional[str]) -> Mapping:
        return self if opening_brace_prefix is self._opening_brace_prefix else replace(self, _opening_brace_prefix=opening_brace_prefix)

    _entries: List[Entry]

    @property
    def entries(self) -> List[Entry]:
        return self._entries

    def with_entries(self, entries: List[Entry]) -> Mapping:
        return self if entries is self._entries else replace(self, _entries=entries)

    _closing_brace_prefix: Optional[str]

    @property
    def closing_brace_prefix(self) -> Optional[str]:
        return self._closing_brace_prefix

    def with_closing_brace_prefix(self, closing_brace_prefix: Optional[str]) -> Mapping:
        return self if closing_brace_prefix is self._closing_brace_prefix else replace(self, _closing_brace_prefix=closing_brace_prefix)

    _anchor: Optional[Anchor]

    @property
    def anchor(self) -> Optional[Anchor]:
        return self._anchor

    def with_anchor(self, anchor: Optional[Anchor]) -> Mapping:
        return self if anchor is self._anchor else replace(self, _anchor=anchor)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class Entry(Yaml):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Mapping.Entry:
            return self if id is self._id else replace(self, _id=id)

        _prefix: str

        @property
        def prefix(self) -> str:
            return self._prefix

        def with_prefix(self, prefix: str) -> Mapping.Entry:
            return self if prefix is self._prefix else replace(self, _prefix=prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Mapping.Entry:
            return self if markers is self._markers else replace(self, _markers=markers)

        _key: YamlKey

        @property
        def key(self) -> YamlKey:
            return self._key

        def with_key(self, key: YamlKey) -> Mapping.Entry:
            return self if key is self._key else replace(self, _key=key)

        _before_mapping_value_indicator: str

        @property
        def before_mapping_value_indicator(self) -> str:
            return self._before_mapping_value_indicator

        def with_before_mapping_value_indicator(self, before_mapping_value_indicator: str) -> Mapping.Entry:
            return self if before_mapping_value_indicator is self._before_mapping_value_indicator else replace(self, _before_mapping_value_indicator=before_mapping_value_indicator)

        _value: Block

        @property
        def value(self) -> Block:
            return self._value

        def with_value(self, value: Block) -> Mapping.Entry:
            return self if value is self._value else replace(self, _value=value)

        def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
            return v.visit_mapping_entry(self, p)

    def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
        return v.visit_mapping(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Sequence(Block):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Sequence:
        return self if id is self._id else replace(self, _id=id)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Sequence:
        return self if markers is self._markers else replace(self, _markers=markers)

    _opening_bracket_prefix: Optional[str]

    @property
    def opening_bracket_prefix(self) -> Optional[str]:
        return self._opening_bracket_prefix

    def with_opening_bracket_prefix(self, opening_bracket_prefix: Optional[str]) -> Sequence:
        return self if opening_bracket_prefix is self._opening_bracket_prefix else replace(self, _opening_bracket_prefix=opening_bracket_prefix)

    _entries: List[Entry]

    @property
    def entries(self) -> List[Entry]:
        return self._entries

    def with_entries(self, entries: List[Entry]) -> Sequence:
        return self if entries is self._entries else replace(self, _entries=entries)

    _closing_bracket_prefix: Optional[str]

    @property
    def closing_bracket_prefix(self) -> Optional[str]:
        return self._closing_bracket_prefix

    def with_closing_bracket_prefix(self, closing_bracket_prefix: Optional[str]) -> Sequence:
        return self if closing_bracket_prefix is self._closing_bracket_prefix else replace(self, _closing_bracket_prefix=closing_bracket_prefix)

    _anchor: Optional[Anchor]

    @property
    def anchor(self) -> Optional[Anchor]:
        return self._anchor

    def with_anchor(self, anchor: Optional[Anchor]) -> Sequence:
        return self if anchor is self._anchor else replace(self, _anchor=anchor)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class Entry(Yaml):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Sequence.Entry:
            return self if id is self._id else replace(self, _id=id)

        _prefix: str

        @property
        def prefix(self) -> str:
            return self._prefix

        def with_prefix(self, prefix: str) -> Sequence.Entry:
            return self if prefix is self._prefix else replace(self, _prefix=prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Sequence.Entry:
            return self if markers is self._markers else replace(self, _markers=markers)

        _block: Block

        @property
        def block(self) -> Block:
            return self._block

        def with_block(self, block: Block) -> Sequence.Entry:
            return self if block is self._block else replace(self, _block=block)

        _dash: bool

        @property
        def dash(self) -> bool:
            return self._dash

        def with_dash(self, dash: bool) -> Sequence.Entry:
            return self if dash is self._dash else replace(self, _dash=dash)

        _trailing_comma_prefix: Optional[str]

        @property
        def trailing_comma_prefix(self) -> Optional[str]:
            return self._trailing_comma_prefix

        def with_trailing_comma_prefix(self, trailing_comma_prefix: Optional[str]) -> Sequence.Entry:
            return self if trailing_comma_prefix is self._trailing_comma_prefix else replace(self, _trailing_comma_prefix=trailing_comma_prefix)

        def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
            return v.visit_sequence_entry(self, p)

    def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
        return v.visit_sequence(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Alias(Block, YamlKey):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Alias:
        return self if id is self._id else replace(self, _id=id)

    _prefix: str

    @property
    def prefix(self) -> str:
        return self._prefix

    def with_prefix(self, prefix: str) -> Alias:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Alias:
        return self if markers is self._markers else replace(self, _markers=markers)

    _anchor: Anchor

    @property
    def anchor(self) -> Anchor:
        return self._anchor

    def with_anchor(self, anchor: Anchor) -> Alias:
        return self if anchor is self._anchor else replace(self, _anchor=anchor)

    def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
        return v.visit_alias(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Anchor(Yaml):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Anchor:
        return self if id is self._id else replace(self, _id=id)

    _prefix: str

    @property
    def prefix(self) -> str:
        return self._prefix

    def with_prefix(self, prefix: str) -> Anchor:
        return self if prefix is self._prefix else replace(self, _prefix=prefix)

    _postfix: str

    @property
    def postfix(self) -> str:
        return self._postfix

    def with_postfix(self, postfix: str) -> Anchor:
        return self if postfix is self._postfix else replace(self, _postfix=postfix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Anchor:
        return self if markers is self._markers else replace(self, _markers=markers)

    _key: str

    @property
    def key(self) -> str:
        return self._key

    def with_key(self, key: str) -> Anchor:
        return self if key is self._key else replace(self, _key=key)

    def accept_yaml(self, v: YamlVisitor[P], p: P) -> Yaml:
        return v.visit_anchor(self, p)
