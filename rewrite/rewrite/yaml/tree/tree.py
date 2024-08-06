from __future__ import annotations
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol
from uuid import UUID
from enum import Enum

from .additional_types import *
from ...core import Checksum, FileAttributes, SourceFile, Tree
from ...core.marker.markers import Markers

class Yaml(Tree, Protocol):
    pass

@dataclass(frozen=True, eq=False)
class Documents(Yaml, SourceFile["Documents"]):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Documents:
        return self if id is self._id else Documents(self._id, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._documents)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Documents:
        return self if markers is self._markers else Documents(self._id, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._documents)

    _source_path: Path

    @property
    def source_path(self) -> Path:
        return self._source_path

    def with_source_path(self, source_path: Path) -> Documents:
        return self if source_path is self._source_path else Documents(self._id, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._documents)

    _file_attributes: Optional[FileAttributes]

    @property
    def file_attributes(self) -> Optional[FileAttributes]:
        return self._file_attributes

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> Documents:
        return self if file_attributes is self._file_attributes else Documents(self._id, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._documents)

    _charset_name: Optional[str]

    @property
    def charset_name(self) -> Optional[str]:
        return self._charset_name

    def with_charset_name(self, charset_name: Optional[str]) -> Documents:
        return self if charset_name is self._charset_name else Documents(self._id, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._documents)

    _charset_bom_marked: bool

    @property
    def charset_bom_marked(self) -> bool:
        return self._charset_bom_marked

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> Documents:
        return self if charset_bom_marked is self._charset_bom_marked else Documents(self._id, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._documents)

    _checksum: Optional[Checksum]

    @property
    def checksum(self) -> Optional[Checksum]:
        return self._checksum

    def with_checksum(self, checksum: Optional[Checksum]) -> Documents:
        return self if checksum is self._checksum else Documents(self._id, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._documents)

    _documents: List[Document]

    @property
    def documents(self) -> List[Document]:
        return self._documents

    def with_documents(self, documents: List[Document]) -> Documents:
        return self if documents is self._documents else Documents(self._id, self._markers, self._source_path, self._file_attributes, self._charset_name, self._charset_bom_marked, self._checksum, self._documents)

@dataclass(frozen=True, eq=False)
class Document(Yaml):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Document:
        return self if id is self._id else Document(self._id, self._prefix, self._markers, self._explicit, self._block, self._end)

    _prefix: str

    @property
    def prefix(self) -> str:
        return self._prefix

    def with_prefix(self, prefix: str) -> Document:
        return self if prefix is self._prefix else Document(self._id, self._prefix, self._markers, self._explicit, self._block, self._end)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Document:
        return self if markers is self._markers else Document(self._id, self._prefix, self._markers, self._explicit, self._block, self._end)

    _explicit: bool

    @property
    def explicit(self) -> bool:
        return self._explicit

    def with_explicit(self, explicit: bool) -> Document:
        return self if explicit is self._explicit else Document(self._id, self._prefix, self._markers, self._explicit, self._block, self._end)

    _block: Block

    @property
    def block(self) -> Block:
        return self._block

    def with_block(self, block: Block) -> Document:
        return self if block is self._block else Document(self._id, self._prefix, self._markers, self._explicit, self._block, self._end)

    _end: End

    @property
    def end(self) -> End:
        return self._end

    def with_end(self, end: End) -> Document:
        return self if end is self._end else Document(self._id, self._prefix, self._markers, self._explicit, self._block, self._end)

    @dataclass(frozen=True, eq=False)
    class End(Yaml):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Document.End:
            return self if id is self._id else Document.End(self._id, self._prefix, self._markers, self._explicit)

        _prefix: str

        @property
        def prefix(self) -> str:
            return self._prefix

        def with_prefix(self, prefix: str) -> Document.End:
            return self if prefix is self._prefix else Document.End(self._id, self._prefix, self._markers, self._explicit)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Document.End:
            return self if markers is self._markers else Document.End(self._id, self._prefix, self._markers, self._explicit)

        _explicit: bool

        @property
        def explicit(self) -> bool:
            return self._explicit

        def with_explicit(self, explicit: bool) -> Document.End:
            return self if explicit is self._explicit else Document.End(self._id, self._prefix, self._markers, self._explicit)

@dataclass(frozen=True, eq=False)
class Block(Yaml):
    pass

@dataclass(frozen=True, eq=False)
class Scalar(Block, YamlKey):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Scalar:
        return self if id is self._id else Scalar(self._id, self._prefix, self._markers, self._style, self._anchor, self._value)

    _prefix: str

    @property
    def prefix(self) -> str:
        return self._prefix

    def with_prefix(self, prefix: str) -> Scalar:
        return self if prefix is self._prefix else Scalar(self._id, self._prefix, self._markers, self._style, self._anchor, self._value)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Scalar:
        return self if markers is self._markers else Scalar(self._id, self._prefix, self._markers, self._style, self._anchor, self._value)

    _style: Style

    @property
    def style(self) -> Style:
        return self._style

    def with_style(self, style: Style) -> Scalar:
        return self if style is self._style else Scalar(self._id, self._prefix, self._markers, self._style, self._anchor, self._value)

    _anchor: Optional[Anchor]

    @property
    def anchor(self) -> Optional[Anchor]:
        return self._anchor

    def with_anchor(self, anchor: Optional[Anchor]) -> Scalar:
        return self if anchor is self._anchor else Scalar(self._id, self._prefix, self._markers, self._style, self._anchor, self._value)

    _value: str

    @property
    def value(self) -> str:
        return self._value

    def with_value(self, value: str) -> Scalar:
        return self if value is self._value else Scalar(self._id, self._prefix, self._markers, self._style, self._anchor, self._value)

    class Style(Enum):
        DOUBLE_QUOTED = 0
        SINGLE_QUOTED = 1
        LITERAL = 2
        FOLDED = 3
        PLAIN = 4

@dataclass(frozen=True, eq=False)
class Mapping(Block):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Mapping:
        return self if id is self._id else Mapping(self._id, self._markers, self._opening_brace_prefix, self._entries, self._closing_brace_prefix, self._anchor)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Mapping:
        return self if markers is self._markers else Mapping(self._id, self._markers, self._opening_brace_prefix, self._entries, self._closing_brace_prefix, self._anchor)

    _opening_brace_prefix: Optional[str]

    @property
    def opening_brace_prefix(self) -> Optional[str]:
        return self._opening_brace_prefix

    def with_opening_brace_prefix(self, opening_brace_prefix: Optional[str]) -> Mapping:
        return self if opening_brace_prefix is self._opening_brace_prefix else Mapping(self._id, self._markers, self._opening_brace_prefix, self._entries, self._closing_brace_prefix, self._anchor)

    _entries: List[Entry]

    @property
    def entries(self) -> List[Entry]:
        return self._entries

    def with_entries(self, entries: List[Entry]) -> Mapping:
        return self if entries is self._entries else Mapping(self._id, self._markers, self._opening_brace_prefix, self._entries, self._closing_brace_prefix, self._anchor)

    _closing_brace_prefix: Optional[str]

    @property
    def closing_brace_prefix(self) -> Optional[str]:
        return self._closing_brace_prefix

    def with_closing_brace_prefix(self, closing_brace_prefix: Optional[str]) -> Mapping:
        return self if closing_brace_prefix is self._closing_brace_prefix else Mapping(self._id, self._markers, self._opening_brace_prefix, self._entries, self._closing_brace_prefix, self._anchor)

    _anchor: Optional[Anchor]

    @property
    def anchor(self) -> Optional[Anchor]:
        return self._anchor

    def with_anchor(self, anchor: Optional[Anchor]) -> Mapping:
        return self if anchor is self._anchor else Mapping(self._id, self._markers, self._opening_brace_prefix, self._entries, self._closing_brace_prefix, self._anchor)

    @dataclass(frozen=True, eq=False)
    class Entry(Yaml):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Mapping.Entry:
            return self if id is self._id else Mapping.Entry(self._id, self._prefix, self._markers, self._key, self._before_mapping_value_indicator, self._value)

        _prefix: str

        @property
        def prefix(self) -> str:
            return self._prefix

        def with_prefix(self, prefix: str) -> Mapping.Entry:
            return self if prefix is self._prefix else Mapping.Entry(self._id, self._prefix, self._markers, self._key, self._before_mapping_value_indicator, self._value)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Mapping.Entry:
            return self if markers is self._markers else Mapping.Entry(self._id, self._prefix, self._markers, self._key, self._before_mapping_value_indicator, self._value)

        _key: YamlKey

        @property
        def key(self) -> YamlKey:
            return self._key

        def with_key(self, key: YamlKey) -> Mapping.Entry:
            return self if key is self._key else Mapping.Entry(self._id, self._prefix, self._markers, self._key, self._before_mapping_value_indicator, self._value)

        _before_mapping_value_indicator: str

        @property
        def before_mapping_value_indicator(self) -> str:
            return self._before_mapping_value_indicator

        def with_before_mapping_value_indicator(self, before_mapping_value_indicator: str) -> Mapping.Entry:
            return self if before_mapping_value_indicator is self._before_mapping_value_indicator else Mapping.Entry(self._id, self._prefix, self._markers, self._key, self._before_mapping_value_indicator, self._value)

        _value: Block

        @property
        def value(self) -> Block:
            return self._value

        def with_value(self, value: Block) -> Mapping.Entry:
            return self if value is self._value else Mapping.Entry(self._id, self._prefix, self._markers, self._key, self._before_mapping_value_indicator, self._value)

@dataclass(frozen=True, eq=False)
class Sequence(Block):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Sequence:
        return self if id is self._id else Sequence(self._id, self._markers, self._opening_bracket_prefix, self._entries, self._closing_bracket_prefix, self._anchor)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Sequence:
        return self if markers is self._markers else Sequence(self._id, self._markers, self._opening_bracket_prefix, self._entries, self._closing_bracket_prefix, self._anchor)

    _opening_bracket_prefix: Optional[str]

    @property
    def opening_bracket_prefix(self) -> Optional[str]:
        return self._opening_bracket_prefix

    def with_opening_bracket_prefix(self, opening_bracket_prefix: Optional[str]) -> Sequence:
        return self if opening_bracket_prefix is self._opening_bracket_prefix else Sequence(self._id, self._markers, self._opening_bracket_prefix, self._entries, self._closing_bracket_prefix, self._anchor)

    _entries: List[Entry]

    @property
    def entries(self) -> List[Entry]:
        return self._entries

    def with_entries(self, entries: List[Entry]) -> Sequence:
        return self if entries is self._entries else Sequence(self._id, self._markers, self._opening_bracket_prefix, self._entries, self._closing_bracket_prefix, self._anchor)

    _closing_bracket_prefix: Optional[str]

    @property
    def closing_bracket_prefix(self) -> Optional[str]:
        return self._closing_bracket_prefix

    def with_closing_bracket_prefix(self, closing_bracket_prefix: Optional[str]) -> Sequence:
        return self if closing_bracket_prefix is self._closing_bracket_prefix else Sequence(self._id, self._markers, self._opening_bracket_prefix, self._entries, self._closing_bracket_prefix, self._anchor)

    _anchor: Optional[Anchor]

    @property
    def anchor(self) -> Optional[Anchor]:
        return self._anchor

    def with_anchor(self, anchor: Optional[Anchor]) -> Sequence:
        return self if anchor is self._anchor else Sequence(self._id, self._markers, self._opening_bracket_prefix, self._entries, self._closing_bracket_prefix, self._anchor)

    @dataclass(frozen=True, eq=False)
    class Entry(Yaml):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Sequence.Entry:
            return self if id is self._id else Sequence.Entry(self._id, self._prefix, self._markers, self._block, self._dash, self._trailing_comma_prefix)

        _prefix: str

        @property
        def prefix(self) -> str:
            return self._prefix

        def with_prefix(self, prefix: str) -> Sequence.Entry:
            return self if prefix is self._prefix else Sequence.Entry(self._id, self._prefix, self._markers, self._block, self._dash, self._trailing_comma_prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Sequence.Entry:
            return self if markers is self._markers else Sequence.Entry(self._id, self._prefix, self._markers, self._block, self._dash, self._trailing_comma_prefix)

        _block: Block

        @property
        def block(self) -> Block:
            return self._block

        def with_block(self, block: Block) -> Sequence.Entry:
            return self if block is self._block else Sequence.Entry(self._id, self._prefix, self._markers, self._block, self._dash, self._trailing_comma_prefix)

        _dash: bool

        @property
        def dash(self) -> bool:
            return self._dash

        def with_dash(self, dash: bool) -> Sequence.Entry:
            return self if dash is self._dash else Sequence.Entry(self._id, self._prefix, self._markers, self._block, self._dash, self._trailing_comma_prefix)

        _trailing_comma_prefix: Optional[str]

        @property
        def trailing_comma_prefix(self) -> Optional[str]:
            return self._trailing_comma_prefix

        def with_trailing_comma_prefix(self, trailing_comma_prefix: Optional[str]) -> Sequence.Entry:
            return self if trailing_comma_prefix is self._trailing_comma_prefix else Sequence.Entry(self._id, self._prefix, self._markers, self._block, self._dash, self._trailing_comma_prefix)

@dataclass(frozen=True, eq=False)
class Alias(Block, YamlKey):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Alias:
        return self if id is self._id else Alias(self._id, self._prefix, self._markers, self._anchor)

    _prefix: str

    @property
    def prefix(self) -> str:
        return self._prefix

    def with_prefix(self, prefix: str) -> Alias:
        return self if prefix is self._prefix else Alias(self._id, self._prefix, self._markers, self._anchor)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Alias:
        return self if markers is self._markers else Alias(self._id, self._prefix, self._markers, self._anchor)

    _anchor: Anchor

    @property
    def anchor(self) -> Anchor:
        return self._anchor

    def with_anchor(self, anchor: Anchor) -> Alias:
        return self if anchor is self._anchor else Alias(self._id, self._prefix, self._markers, self._anchor)

@dataclass(frozen=True, eq=False)
class Anchor(Yaml):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Anchor:
        return self if id is self._id else Anchor(self._id, self._prefix, self._postfix, self._markers, self._key)

    _prefix: str

    @property
    def prefix(self) -> str:
        return self._prefix

    def with_prefix(self, prefix: str) -> Anchor:
        return self if prefix is self._prefix else Anchor(self._id, self._prefix, self._postfix, self._markers, self._key)

    _postfix: str

    @property
    def postfix(self) -> str:
        return self._postfix

    def with_postfix(self, postfix: str) -> Anchor:
        return self if postfix is self._postfix else Anchor(self._id, self._prefix, self._postfix, self._markers, self._key)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Anchor:
        return self if markers is self._markers else Anchor(self._id, self._prefix, self._postfix, self._markers, self._key)

    _key: str

    @property
    def key(self) -> str:
        return self._key

    def with_key(self, key: str) -> Anchor:
        return self if key is self._key else Anchor(self._id, self._prefix, self._postfix, self._markers, self._key)
