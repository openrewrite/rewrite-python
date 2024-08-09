from __future__ import annotations

import weakref
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol, runtime_checkable
from uuid import UUID
from enum import Enum

from .support_types import *
from rewrite import Checksum, FileAttributes, SourceFile, Tree, TreeVisitor
from rewrite.marker import Markers

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

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Document:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

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

    _prolog: Prolog

    @property
    def prolog(self) -> Prolog:
        return self._prolog

    def with_prolog(self, prolog: Prolog) -> Document:
        return self if prolog is self._prolog else replace(self, _prolog=prolog)

    _root: Tag

    @property
    def root(self) -> Tag:
        return self._root

    def with_root(self, root: Tag) -> Document:
        return self if root is self._root else replace(self, _root=root)

    _eof: str

    @property
    def eof(self) -> str:
        return self._eof

    def with_eof(self, eof: str) -> Document:
        return self if eof is self._eof else replace(self, _eof=eof)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_document(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Prolog:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Prolog:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Prolog:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Prolog:
        return self if markers is self._markers else replace(self, _markers=markers)

    _xml_decl: Optional[XmlDecl]

    @property
    def xml_decl(self) -> Optional[XmlDecl]:
        return self._xml_decl

    def with_xml_decl(self, xml_decl: Optional[XmlDecl]) -> Prolog:
        return self if xml_decl is self._xml_decl else replace(self, _xml_decl=xml_decl)

    _misc: List[Misc]

    @property
    def misc(self) -> List[Misc]:
        return self._misc

    def with_misc(self, misc: List[Misc]) -> Prolog:
        return self if misc is self._misc else replace(self, _misc=misc)

    _jsp_directives: List[JspDirective]

    @property
    def jsp_directives(self) -> List[JspDirective]:
        return self._jsp_directives

    def with_jsp_directives(self, jsp_directives: List[JspDirective]) -> Prolog:
        return self if jsp_directives is self._jsp_directives else replace(self, _jsp_directives=jsp_directives)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_prolog(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class XmlDecl(Misc):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> XmlDecl:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> XmlDecl:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> XmlDecl:
        return self if markers is self._markers else replace(self, _markers=markers)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> XmlDecl:
        return self if name is self._name else replace(self, _name=name)

    _attributes: List[Attribute]

    @property
    def attributes(self) -> List[Attribute]:
        return self._attributes

    def with_attributes(self, attributes: List[Attribute]) -> XmlDecl:
        return self if attributes is self._attributes else replace(self, _attributes=attributes)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> XmlDecl:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else replace(self, _before_tag_delimiter_prefix=before_tag_delimiter_prefix)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_xml_decl(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class ProcessingInstruction(Content, Misc):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> ProcessingInstruction:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> ProcessingInstruction:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> ProcessingInstruction:
        return self if markers is self._markers else replace(self, _markers=markers)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> ProcessingInstruction:
        return self if name is self._name else replace(self, _name=name)

    _processing_instructions: CharData

    @property
    def processing_instructions(self) -> CharData:
        return self._processing_instructions

    def with_processing_instructions(self, processing_instructions: CharData) -> ProcessingInstruction:
        return self if processing_instructions is self._processing_instructions else replace(self, _processing_instructions=processing_instructions)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> ProcessingInstruction:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else replace(self, _before_tag_delimiter_prefix=before_tag_delimiter_prefix)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_processing_instruction(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Tag(Content):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Tag:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Tag:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Tag:
        return self if markers is self._markers else replace(self, _markers=markers)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> Tag:
        return self if name is self._name else replace(self, _name=name)

    _attributes: List[Attribute]

    @property
    def attributes(self) -> List[Attribute]:
        return self._attributes

    def with_attributes(self, attributes: List[Attribute]) -> Tag:
        return self if attributes is self._attributes else replace(self, _attributes=attributes)

    _content: Optional[List[Content]]

    @property
    def content(self) -> Optional[List[Content]]:
        return self._content

    def with_content(self, content: Optional[List[Content]]) -> Tag:
        return self if content is self._content else replace(self, _content=content)

    _closing: Optional[Closing]

    @property
    def closing(self) -> Optional[Closing]:
        return self._closing

    def with_closing(self, closing: Optional[Closing]) -> Tag:
        return self if closing is self._closing else replace(self, _closing=closing)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> Tag:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else replace(self, _before_tag_delimiter_prefix=before_tag_delimiter_prefix)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class Closing:
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Tag.Closing:
            return self if id is self._id else replace(self, _id=id)

        _prefix_unsafe: str

        @property
        def prefix_unsafe(self) -> str:
            return self._prefix_unsafe

        def with_prefix_unsafe(self, prefix_unsafe: str) -> Tag.Closing:
            return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Tag.Closing:
            return self if markers is self._markers else replace(self, _markers=markers)

        _name: str

        @property
        def name(self) -> str:
            return self._name

        def with_name(self, name: str) -> Tag.Closing:
            return self if name is self._name else replace(self, _name=name)

        _before_tag_delimiter_prefix: str

        @property
        def before_tag_delimiter_prefix(self) -> str:
            return self._before_tag_delimiter_prefix

        def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> Tag.Closing:
            return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else replace(self, _before_tag_delimiter_prefix=before_tag_delimiter_prefix)

        def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
            # noinspection PyUnresolvedReferences
            return v.visit_tag_closing(self, p)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_tag(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Attribute:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Attribute:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Attribute:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Attribute:
        return self if markers is self._markers else replace(self, _markers=markers)

    _key: Ident

    @property
    def key(self) -> Ident:
        return self._key

    def with_key(self, key: Ident) -> Attribute:
        return self if key is self._key else replace(self, _key=key)

    _before_equals: str

    @property
    def before_equals(self) -> str:
        return self._before_equals

    def with_before_equals(self, before_equals: str) -> Attribute:
        return self if before_equals is self._before_equals else replace(self, _before_equals=before_equals)

    _value: Value

    @property
    def value(self) -> Value:
        return self._value

    def with_value(self, value: Value) -> Attribute:
        return self if value is self._value else replace(self, _value=value)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class Value:
        class Quote(Enum):
            Double = 0
            Single = 1

        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> Attribute.Value:
            return self if id is self._id else replace(self, _id=id)

        _prefix_unsafe: str

        @property
        def prefix_unsafe(self) -> str:
            return self._prefix_unsafe

        def with_prefix_unsafe(self, prefix_unsafe: str) -> Attribute.Value:
            return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> Attribute.Value:
            return self if markers is self._markers else replace(self, _markers=markers)

        _quote: Quote

        @property
        def quote(self) -> Quote:
            return self._quote

        def with_quote(self, quote: Quote) -> Attribute.Value:
            return self if quote is self._quote else replace(self, _quote=quote)

        _value: str

        @property
        def value(self) -> str:
            return self._value

        def with_value(self, value: str) -> Attribute.Value:
            return self if value is self._value else replace(self, _value=value)

        def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
            # noinspection PyUnresolvedReferences
            return v.visit_attribute_value(self, p)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_attribute(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class CharData(Content):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> CharData:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> CharData:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> CharData:
        return self if markers is self._markers else replace(self, _markers=markers)

    _cdata: bool

    @property
    def cdata(self) -> bool:
        return self._cdata

    def with_cdata(self, cdata: bool) -> CharData:
        return self if cdata is self._cdata else replace(self, _cdata=cdata)

    _text: str

    @property
    def text(self) -> str:
        return self._text

    def with_text(self, text: str) -> CharData:
        return self if text is self._text else replace(self, _text=text)

    _after_text: str

    @property
    def after_text(self) -> str:
        return self._after_text

    def with_after_text(self, after_text: str) -> CharData:
        return self if after_text is self._after_text else replace(self, _after_text=after_text)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_char_data(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Comment(Content, Misc):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Comment:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Comment:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Comment:
        return self if markers is self._markers else replace(self, _markers=markers)

    _text: str

    @property
    def text(self) -> str:
        return self._text

    def with_text(self, text: str) -> Comment:
        return self if text is self._text else replace(self, _text=text)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_comment(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class DocTypeDecl(Misc):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> DocTypeDecl:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> DocTypeDecl:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> DocTypeDecl:
        return self if markers is self._markers else replace(self, _markers=markers)

    _name: Ident

    @property
    def name(self) -> Ident:
        return self._name

    def with_name(self, name: Ident) -> DocTypeDecl:
        return self if name is self._name else replace(self, _name=name)

    _external_id: Optional[Ident]

    @property
    def external_id(self) -> Optional[Ident]:
        return self._external_id

    def with_external_id(self, external_id: Optional[Ident]) -> DocTypeDecl:
        return self if external_id is self._external_id else replace(self, _external_id=external_id)

    _internal_subset: List[Ident]

    @property
    def internal_subset(self) -> List[Ident]:
        return self._internal_subset

    def with_internal_subset(self, internal_subset: List[Ident]) -> DocTypeDecl:
        return self if internal_subset is self._internal_subset else replace(self, _internal_subset=internal_subset)

    _external_subsets: Optional[ExternalSubsets]

    @property
    def external_subsets(self) -> Optional[ExternalSubsets]:
        return self._external_subsets

    def with_external_subsets(self, external_subsets: Optional[ExternalSubsets]) -> DocTypeDecl:
        return self if external_subsets is self._external_subsets else replace(self, _external_subsets=external_subsets)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> DocTypeDecl:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else replace(self, _before_tag_delimiter_prefix=before_tag_delimiter_prefix)

    # noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
    @dataclass(frozen=True, eq=False)
    class ExternalSubsets:
        _id: UUID

        @property
        def id(self) -> UUID:
            return self._id

        def with_id(self, id: UUID) -> DocTypeDecl.ExternalSubsets:
            return self if id is self._id else replace(self, _id=id)

        _prefix_unsafe: str

        @property
        def prefix_unsafe(self) -> str:
            return self._prefix_unsafe

        def with_prefix_unsafe(self, prefix_unsafe: str) -> DocTypeDecl.ExternalSubsets:
            return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

        _markers: Markers

        @property
        def markers(self) -> Markers:
            return self._markers

        def with_markers(self, markers: Markers) -> DocTypeDecl.ExternalSubsets:
            return self if markers is self._markers else replace(self, _markers=markers)

        _elements: List[Element]

        @property
        def elements(self) -> List[Element]:
            return self._elements

        def with_elements(self, elements: List[Element]) -> DocTypeDecl.ExternalSubsets:
            return self if elements is self._elements else replace(self, _elements=elements)

        def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
            # noinspection PyUnresolvedReferences
            return v.visit_doc_type_decl_external_subsets(self, p)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_doc_type_decl(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Element:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Element:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Element:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Element:
        return self if markers is self._markers else replace(self, _markers=markers)

    _subset: List[Ident]

    @property
    def subset(self) -> List[Ident]:
        return self._subset

    def with_subset(self, subset: List[Ident]) -> Element:
        return self if subset is self._subset else replace(self, _subset=subset)

    _before_tag_delimiter_prefix: str

    @property
    def before_tag_delimiter_prefix(self) -> str:
        return self._before_tag_delimiter_prefix

    def with_before_tag_delimiter_prefix(self, before_tag_delimiter_prefix: str) -> Element:
        return self if before_tag_delimiter_prefix is self._before_tag_delimiter_prefix else replace(self, _before_tag_delimiter_prefix=before_tag_delimiter_prefix)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_element(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class Ident:
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> Ident:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> Ident:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> Ident:
        return self if markers is self._markers else replace(self, _markers=markers)

    _name: str

    @property
    def name(self) -> str:
        return self._name

    def with_name(self, name: str) -> Ident:
        return self if name is self._name else replace(self, _name=name)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_ident(self, p)

# noinspection PyShadowingBuiltins,PyShadowingNames,DuplicatedCode
@dataclass(frozen=True, eq=False)
class JspDirective(Content):
    _id: UUID

    @property
    def id(self) -> UUID:
        return self._id

    def with_id(self, id: UUID) -> JspDirective:
        return self if id is self._id else replace(self, _id=id)

    _prefix_unsafe: str

    @property
    def prefix_unsafe(self) -> str:
        return self._prefix_unsafe

    def with_prefix_unsafe(self, prefix_unsafe: str) -> JspDirective:
        return self if prefix_unsafe is self._prefix_unsafe else replace(self, _prefix_unsafe=prefix_unsafe)

    _markers: Markers

    @property
    def markers(self) -> Markers:
        return self._markers

    def with_markers(self, markers: Markers) -> JspDirective:
        return self if markers is self._markers else replace(self, _markers=markers)

    _before_type_prefix: str

    @property
    def before_type_prefix(self) -> str:
        return self._before_type_prefix

    def with_before_type_prefix(self, before_type_prefix: str) -> JspDirective:
        return self if before_type_prefix is self._before_type_prefix else replace(self, _before_type_prefix=before_type_prefix)

    _type: str

    @property
    def type(self) -> str:
        return self._type

    def with_type(self, type: str) -> JspDirective:
        return self if type is self._type else replace(self, _type=type)

    _attributes: List[Attribute]

    @property
    def attributes(self) -> List[Attribute]:
        return self._attributes

    def with_attributes(self, attributes: List[Attribute]) -> JspDirective:
        return self if attributes is self._attributes else replace(self, _attributes=attributes)

    _before_directive_end_prefix: str

    @property
    def before_directive_end_prefix(self) -> str:
        return self._before_directive_end_prefix

    def with_before_directive_end_prefix(self, before_directive_end_prefix: str) -> JspDirective:
        return self if before_directive_end_prefix is self._before_directive_end_prefix else replace(self, _before_directive_end_prefix=before_directive_end_prefix)

    def accept_xml(self, v: TreeVisitor[Xml, P], p: P) -> Xml:
        # noinspection PyUnresolvedReferences
        return v.visit_jsp_directive(self, p)
