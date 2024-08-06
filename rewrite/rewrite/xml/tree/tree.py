from __future__ import annotations
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol
from uuid import UUID
from enum import Enum

from .additional_types import *
from ...core import Checksum, FileAttributes, SourceFile, Tree
from ...core.marker.markers import Markers

class Xml(Tree, Protocol):
    pass

@dataclass(frozen=True, eq=False)
class Document(Xml, SourceFile["Document"]):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Document:
        return self if id is self._id else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _source_path: Path

    @property
    def source_path(self) -> Path:
        return self._source_path

    def with_source_path(self, source_path: Path) -> Document:
        return self if source_path is self._source_path else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Document:
        return self if prefix_unsafe is self._prefix_unsafe else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Document:
        return self if markers is self._markers else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _charset_name: Optional[str]

    @property
    def charset_name(self) -> Optional[str]:
        return self._charset_name

    def with_charset_name(self, charset_name: Optional[str]) -> Document:
        return self if charset_name is self._charset_name else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _charset_bom_marked: bool

    @property
    def charset_bom_marked(self) -> bool:
        return self._charset_bom_marked

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> Document:
        return self if charset_bom_marked is self._charset_bom_marked else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _checksum: Optional[Checksum]

    @property
    def checksum(self) -> Optional[Checksum]:
        return self._checksum

    def with_checksum(self, checksum: Optional[Checksum]) -> Document:
        return self if checksum is self._checksum else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _file_attributes: Optional[FileAttributes]

    @property
    def file_attributes(self) -> Optional[FileAttributes]:
        return self._file_attributes

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> Document:
        return self if file_attributes is self._file_attributes else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _prolog: Prolog

    @property
    def prolog(self) -> Prolog:
        return self._prolog

    def with_prolog(self, prolog: Prolog) -> Document:
        return self if prolog is self._prolog else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _root: Tag

    @property
    def root(self) -> Tag:
        return self._root

    def with_root(self, root: Tag) -> Document:
        return self if root is self._root else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

    _eof: str

    @property
    def eof(self) -> str:
        return self._eof

    def with_eof(self, eof: str) -> Document:
        return self if eof is self._eof else Document(self._id, self._source_path, self._prefix_unsafe, self._markers, self._charset_name, self._charset_bom_marked, self._checksum, self._file_attributes, self._prolog, self._root, self._eof)

@dataclass(frozen=True, eq=False)
class Prolog(Xml):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Prolog:
        return self if id is self._id else Prolog(self._id, self._prefix_unsafe, self._markers, self._xml_decl, self._misc, self._jsp_directives)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Prolog:
        return self if prefix_unsafe is self._prefix_unsafe else Prolog(self._id, self._prefix_unsafe, self._markers, self._xml_decl, self._misc, self._jsp_directives)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Prolog:
        return self if markers is self._markers else Prolog(self._id, self._prefix_unsafe, self._markers, self._xml_decl, self._misc, self._jsp_directives)

    _xml_decl: Optional[XmlDecl]

    @property
    def xml_decl(self) -> Optional[XmlDecl]:
        return self._xml_decl

    def with_xml_decl(self, xml_decl: Optional[XmlDecl]) -> Prolog:
        return self if xml_decl is self._xml_decl else Prolog(self._id, self._prefix_unsafe, self._markers, self._xml_decl, self._misc, self._jsp_directives)

    _misc: List[Misc]

    @property
    def misc(self) -> List[Misc]:
        return self._misc

    def with_misc(self, misc: List[Misc]) -> Prolog:
        return self if misc is self._misc else Prolog(self._id, self._prefix_unsafe, self._markers, self._xml_decl, self._misc, self._jsp_directives)

    _jsp_directives: List[JspDirective]

    @property
    def jsp_directives(self) -> List[JspDirective]:
        return self._jsp_directives

    def with_jsp_directives(self, jsp_directives: List[JspDirective]) -> Prolog:
        return self if jsp_directives is self._jsp_directives else Prolog(self._id, self._prefix_unsafe, self._markers, self._xml_decl, self._misc, self._jsp_directives)

@dataclass(frozen=True, eq=False)
class XmlDecl(Xml, Misc):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> XmlDecl:
        return self if id is self._id else XmlDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._before_tag_delimiter_prefix)

    _prefix_unsafe: str

    @property
    def prefix(self) -> str:
        return self._prefix_unsafe

    def with_prefix(self, prefix_unsafe: str) -> XmlDecl:
        return self if prefix_unsafe is self._prefix_unsafe else XmlDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._before_tag_delimiter_prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> XmlDecl:
        return self if markers is self._markers else XmlDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._before_tag_delimiter_prefix)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> XmlDecl:
        return self if name is self._name else XmlDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._before_tag_delimiter_prefix)

    _attributes: List[Attribute]

    @property
    def attributes(self) -> List[Attribute]:
        return self._attributes

    def with_attributes(self, attributes: List[Attribute]) -> XmlDecl:
        return self if attributes is self._attributes else XmlDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._before_tag_delimiter_prefix)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> XmlDecl:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else XmlDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._before_tag_delimiter_prefix)

@dataclass(frozen=True, eq=False)
class ProcessingInstruction(Xml, Content, Misc):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ProcessingInstruction:
        return self if id is self._id else ProcessingInstruction(self._id, self._prefix_unsafe, self._markers, self._name, self._processing_instructions, self._before_tag_delimiter_prefix)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> ProcessingInstruction:
        return self if prefix_unsafe is self._prefix_unsafe else ProcessingInstruction(self._id, self._prefix_unsafe, self._markers, self._name, self._processing_instructions, self._before_tag_delimiter_prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ProcessingInstruction:
        return self if markers is self._markers else ProcessingInstruction(self._id, self._prefix_unsafe, self._markers, self._name, self._processing_instructions, self._before_tag_delimiter_prefix)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> ProcessingInstruction:
        return self if name is self._name else ProcessingInstruction(self._id, self._prefix_unsafe, self._markers, self._name, self._processing_instructions, self._before_tag_delimiter_prefix)

    _processing_instructions: CharData

    @property
    def processing_instructions(self) -> CharData:
        return self._processing_instructions

    def with_processing_instructions(self, processing_instructions: CharData) -> ProcessingInstruction:
        return self if processing_instructions is self._processing_instructions else ProcessingInstruction(self._id, self._prefix_unsafe, self._markers, self._name, self._processing_instructions, self._before_tag_delimiter_prefix)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> ProcessingInstruction:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else ProcessingInstruction(self._id, self._prefix_unsafe, self._markers, self._name, self._processing_instructions, self._before_tag_delimiter_prefix)

@dataclass(frozen=True, eq=False)
class Tag(Xml, Content):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Tag:
        return self if id is self._id else Tag(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._content, self._closing, self._before_tag_delimiter_prefix)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Tag:
        return self if prefix_unsafe is self._prefix_unsafe else Tag(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._content, self._closing, self._before_tag_delimiter_prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Tag:
        return self if markers is self._markers else Tag(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._content, self._closing, self._before_tag_delimiter_prefix)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> Tag:
        return self if name is self._name else Tag(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._content, self._closing, self._before_tag_delimiter_prefix)

    _attributes: List[Attribute]

    @property
    def attributes(self) -> List[Attribute]:
        return self._attributes

    def with_attributes(self, attributes: List[Attribute]) -> Tag:
        return self if attributes is self._attributes else Tag(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._content, self._closing, self._before_tag_delimiter_prefix)

    _content: Optional[List[Content]]

    @property
    def content(self) -> Optional[List[Content]]:
        return self._content

    def with_content(self, content: Optional[List[Content]]) -> Tag:
        return self if content is self._content else Tag(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._content, self._closing, self._before_tag_delimiter_prefix)

    _closing: Optional[Closing]

    @property
    def closing(self) -> Optional[Closing]:
        return self._closing

    def with_closing(self, closing: Optional[Closing]) -> Tag:
        return self if closing is self._closing else Tag(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._content, self._closing, self._before_tag_delimiter_prefix)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> Tag:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else Tag(self._id, self._prefix_unsafe, self._markers, self._name, self._attributes, self._content, self._closing, self._before_tag_delimiter_prefix)

    @dataclass(frozen=True, eq=False)
    class Closing(Xml):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Tag.Closing:
            return self if id is self._id else Tag.Closing(self._id, self._prefix_unsafe, self._markers, self._name, self._before_tag_delimiter_prefix)

        _prefix_unsafe: str

        @property
        def prefix_unsafe(self) -> str:
            return self._prefix_unsafe

        def with_prefix_unsafe(self, prefix_unsafe: str) -> Tag.Closing:
            return self if prefix_unsafe is self._prefix_unsafe else Tag.Closing(self._id, self._prefix_unsafe, self._markers, self._name, self._before_tag_delimiter_prefix)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Tag.Closing:
            return self if markers is self._markers else Tag.Closing(self._id, self._prefix_unsafe, self._markers, self._name, self._before_tag_delimiter_prefix)

        _name: str

        @property
        def name(self) -> str:
            return self._name

        def with_name(self, name: str) -> Tag.Closing:
            return self if name is self._name else Tag.Closing(self._id, self._prefix_unsafe, self._markers, self._name, self._before_tag_delimiter_prefix)

        _before_tag_delimiter_prefix: str

        @property
        def before_tag_delimiter_prefix(self) -> str:
            return self._before_tag_delimiter_prefix

        def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> Tag.Closing:
            return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else Tag.Closing(self._id, self._prefix_unsafe, self._markers, self._name, self._before_tag_delimiter_prefix)

@dataclass(frozen=True, eq=False)
class Attribute(Xml):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Attribute:
        return self if id is self._id else Attribute(self._id, self._prefix_unsafe, self._markers, self._key, self._before_equals, self._value)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Attribute:
        return self if prefix_unsafe is self._prefix_unsafe else Attribute(self._id, self._prefix_unsafe, self._markers, self._key, self._before_equals, self._value)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Attribute:
        return self if markers is self._markers else Attribute(self._id, self._prefix_unsafe, self._markers, self._key, self._before_equals, self._value)

    _key: Ident

    @property
    def key(self) -> Ident:
        return self._key

    def with_key(self, key: Ident) -> Attribute:
        return self if key is self._key else Attribute(self._id, self._prefix_unsafe, self._markers, self._key, self._before_equals, self._value)

    _before_equals: str

    @property
    def before_equals(self) -> str:
        return self._before_equals

    def with_before_equals(self, before_equals: str) -> Attribute:
        return self if before_equals is self._before_equals else Attribute(self._id, self._prefix_unsafe, self._markers, self._key, self._before_equals, self._value)

    _value: Value

    @property
    def value(self) -> Value:
        return self._value

    def with_value(self, value: Value) -> Attribute:
        return self if value is self._value else Attribute(self._id, self._prefix_unsafe, self._markers, self._key, self._before_equals, self._value)

    @dataclass(frozen=True, eq=False)
    class Value(Xml):
        class Quote(Enum):
            Double = 0
            Single = 1

        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Attribute.Value:
            return self if id is self._id else Attribute.Value(self._id, self._prefix_unsafe, self._markers, self._quote, self._value)

        _prefix_unsafe: str

        @property
        def prefix_unsafe(self) -> str:
            return self._prefix_unsafe

        def with_prefix_unsafe(self, prefix_unsafe: str) -> Attribute.Value:
            return self if prefix_unsafe is self._prefix_unsafe else Attribute.Value(self._id, self._prefix_unsafe, self._markers, self._quote, self._value)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Attribute.Value:
            return self if markers is self._markers else Attribute.Value(self._id, self._prefix_unsafe, self._markers, self._quote, self._value)

        _quote: Quote

        @property
        def quote(self) -> Quote:
            return self._quote

        def with_quote(self, quote: Quote) -> Attribute.Value:
            return self if quote is self._quote else Attribute.Value(self._id, self._prefix_unsafe, self._markers, self._quote, self._value)

        _value: str

        @property
        def value(self) -> str:
            return self._value

        def with_value(self, value: str) -> Attribute.Value:
            return self if value is self._value else Attribute.Value(self._id, self._prefix_unsafe, self._markers, self._quote, self._value)

@dataclass(frozen=True, eq=False)
class CharData(Xml, Content):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> CharData:
        return self if id is self._id else CharData(self._id, self._prefix_unsafe, self._markers, self._cdata, self._text, self._after_text)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> CharData:
        return self if prefix_unsafe is self._prefix_unsafe else CharData(self._id, self._prefix_unsafe, self._markers, self._cdata, self._text, self._after_text)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> CharData:
        return self if markers is self._markers else CharData(self._id, self._prefix_unsafe, self._markers, self._cdata, self._text, self._after_text)

    _cdata: bool

    @property
    def cdata(self) -> bool:
        return self._cdata

    def with_cdata(self, cdata: bool) -> CharData:
        return self if cdata is self._cdata else CharData(self._id, self._prefix_unsafe, self._markers, self._cdata, self._text, self._after_text)

    _text: str

    @property
    def text(self) -> str:
        return self._text

    def with_text(self, text: str) -> CharData:
        return self if text is self._text else CharData(self._id, self._prefix_unsafe, self._markers, self._cdata, self._text, self._after_text)

    _after_text: str

    @property
    def after_text(self) -> str:
        return self._after_text

    def with_after_text(self, after_text: str) -> CharData:
        return self if after_text is self._after_text else CharData(self._id, self._prefix_unsafe, self._markers, self._cdata, self._text, self._after_text)

@dataclass(frozen=True, eq=False)
class Comment(Xml, Content, Misc):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Comment:
        return self if id is self._id else Comment(self._id, self._prefix_unsafe, self._markers, self._text)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Comment:
        return self if prefix_unsafe is self._prefix_unsafe else Comment(self._id, self._prefix_unsafe, self._markers, self._text)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Comment:
        return self if markers is self._markers else Comment(self._id, self._prefix_unsafe, self._markers, self._text)

    _text: str

    @property
    def text(self) -> str:
        return self._text

    def with_text(self, text: str) -> Comment:
        return self if text is self._text else Comment(self._id, self._prefix_unsafe, self._markers, self._text)

@dataclass(frozen=True, eq=False)
class DocTypeDecl(Xml, Misc):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> DocTypeDecl:
        return self if id is self._id else DocTypeDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._external_id, self._internal_subset, self._external_subsets, self._before_tag_delimiter_prefix)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> DocTypeDecl:
        return self if prefix_unsafe is self._prefix_unsafe else DocTypeDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._external_id, self._internal_subset, self._external_subsets, self._before_tag_delimiter_prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> DocTypeDecl:
        return self if markers is self._markers else DocTypeDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._external_id, self._internal_subset, self._external_subsets, self._before_tag_delimiter_prefix)

    _name: Ident

    @property
    def name(self) -> Ident:
        return self._name

    def with_name(self, name: Ident) -> DocTypeDecl:
        return self if name is self._name else DocTypeDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._external_id, self._internal_subset, self._external_subsets, self._before_tag_delimiter_prefix)

    _external_id: Optional[Ident]

    @property
    def external_id(self) -> Optional[Ident]:
        return self._external_id

    def with_external_id(self, external_id: Optional[Ident]) -> DocTypeDecl:
        return self if external_id is self._external_id else DocTypeDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._external_id, self._internal_subset, self._external_subsets, self._before_tag_delimiter_prefix)

    _internal_subset: List[Ident]

    @property
    def internal_subset(self) -> List[Ident]:
        return self._internal_subset

    def with_internal_subset(self, internal_subset: List[Ident]) -> DocTypeDecl:
        return self if internal_subset is self._internal_subset else DocTypeDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._external_id, self._internal_subset, self._external_subsets, self._before_tag_delimiter_prefix)

    _external_subsets: Optional[ExternalSubsets]

    @property
    def external_subsets(self) -> Optional[ExternalSubsets]:
        return self._external_subsets

    def with_external_subsets(self, external_subsets: Optional[ExternalSubsets]) -> DocTypeDecl:
        return self if external_subsets is self._external_subsets else DocTypeDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._external_id, self._internal_subset, self._external_subsets, self._before_tag_delimiter_prefix)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> DocTypeDecl:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else DocTypeDecl(self._id, self._prefix_unsafe, self._markers, self._name, self._external_id, self._internal_subset, self._external_subsets, self._before_tag_delimiter_prefix)

    @dataclass(frozen=True, eq=False)
    class ExternalSubsets(Xml):
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> DocTypeDecl.ExternalSubsets:
            return self if id is self._id else DocTypeDecl.ExternalSubsets(self._id, self._prefix_unsafe, self._markers, self._elements)

        _prefix_unsafe: str

        @property
        def prefix_unsafe(self) -> str:
            return self._prefix_unsafe

        def with_prefix_unsafe(self, prefix_unsafe: str) -> DocTypeDecl.ExternalSubsets:
            return self if prefix_unsafe is self._prefix_unsafe else DocTypeDecl.ExternalSubsets(self._id, self._prefix_unsafe, self._markers, self._elements)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> DocTypeDecl.ExternalSubsets:
            return self if markers is self._markers else DocTypeDecl.ExternalSubsets(self._id, self._prefix_unsafe, self._markers, self._elements)

        _elements: List[Element]

        @property
        def elements(self) -> List[Element]:
            return self._elements

        def with_elements(self, elements: List[Element]) -> DocTypeDecl.ExternalSubsets:
            return self if elements is self._elements else DocTypeDecl.ExternalSubsets(self._id, self._prefix_unsafe, self._markers, self._elements)

@dataclass(frozen=True, eq=False)
class Element(Xml):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Element:
        return self if id is self._id else Element(self._id, self._prefix_unsafe, self._markers, self._subset, self._before_tag_delimiter_prefix)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Element:
        return self if prefix_unsafe is self._prefix_unsafe else Element(self._id, self._prefix_unsafe, self._markers, self._subset, self._before_tag_delimiter_prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Element:
        return self if markers is self._markers else Element(self._id, self._prefix_unsafe, self._markers, self._subset, self._before_tag_delimiter_prefix)

    _subset: List[Ident]

    @property
    def subset(self) -> List[Ident]:
        return self._subset

    def with_subset(self, subset: List[Ident]) -> Element:
        return self if subset is self._subset else Element(self._id, self._prefix_unsafe, self._markers, self._subset, self._before_tag_delimiter_prefix)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> Element:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else Element(self._id, self._prefix_unsafe, self._markers, self._subset, self._before_tag_delimiter_prefix)

@dataclass(frozen=True, eq=False)
class Ident(Xml):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Ident:
        return self if id is self._id else Ident(self._id, self._prefix_unsafe, self._markers, self._name)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Ident:
        return self if prefix_unsafe is self._prefix_unsafe else Ident(self._id, self._prefix_unsafe, self._markers, self._name)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Ident:
        return self if markers is self._markers else Ident(self._id, self._prefix_unsafe, self._markers, self._name)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> Ident:
        return self if name is self._name else Ident(self._id, self._prefix_unsafe, self._markers, self._name)

@dataclass(frozen=True, eq=False)
class JspDirective(Xml, Content):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> JspDirective:
        return self if id is self._id else JspDirective(self._id, self._prefix_unsafe, self._markers, self._before_type_prefix, self._type, self._attributes, self._before_directive_end_prefix)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> JspDirective:
        return self if prefix_unsafe is self._prefix_unsafe else JspDirective(self._id, self._prefix_unsafe, self._markers, self._before_type_prefix, self._type, self._attributes, self._before_directive_end_prefix)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JspDirective:
        return self if markers is self._markers else JspDirective(self._id, self._prefix_unsafe, self._markers, self._before_type_prefix, self._type, self._attributes, self._before_directive_end_prefix)

    _before_type_prefix: str

    @property
    def before_type_prefix(self) -> str:
        return self._before_type_prefix

    def with_before_type_prefix(self, before_type_prefix: str) -> JspDirective:
        return self if before_type_prefix is self._before_type_prefix else JspDirective(self._id, self._prefix_unsafe, self._markers, self._before_type_prefix, self._type, self._attributes, self._before_directive_end_prefix)

    _type: str

    @property
    def type(self) -> str:
        return self._type

    def with_type(self, type: str) -> JspDirective:
        return self if type is self._type else JspDirective(self._id, self._prefix_unsafe, self._markers, self._before_type_prefix, self._type, self._attributes, self._before_directive_end_prefix)

    _attributes: List[Attribute]

    @property
    def attributes(self) -> List[Attribute]:
        return self._attributes

    def with_attributes(self, attributes: List[Attribute]) -> JspDirective:
        return self if attributes is self._attributes else JspDirective(self._id, self._prefix_unsafe, self._markers, self._before_type_prefix, self._type, self._attributes, self._before_directive_end_prefix)

    _before_directive_end_prefix: str

    @property
    def before_directive_end_prefix(self) -> str:
        return self._before_directive_end_prefix

    def with_before_directive_end_prefix(self, before_directive_end_prefix: str) -> JspDirective:
        return self if before_directive_end_prefix is self._before_directive_end_prefix else JspDirective(self._id, self._prefix_unsafe, self._markers, self._before_type_prefix, self._type, self._attributes, self._before_directive_end_prefix)
