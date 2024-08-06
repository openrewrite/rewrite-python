from __future__ import annotations
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Protocol
from uuid import UUID
from enum import Enum

from ...core import Checksum, FileAttributes, SourceFile, Tree
from ...core.marker.markers import Markers

class Yaml(Tree, Protocol):
    pass

@dataclass(frozen=True, eq=False)
class Documents(Yaml, MutableSourceFile<Documents>):
    def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
        return v.VisitDocuments(this, p)

    id: Guid

    def with_id(self, id: Guid) -> Documents:
        return self if id is self.id else Documents(id, self.markers, self.source_path, self.file_attributes, self.charset_name, self.charset_bom_marked, self.checksum, self.documents)

    markers: Markers

    def with_markers(self, markers: Markers) -> Documents:
        return self if markers is self.markers else Documents(self.id, markers, self.source_path, self.file_attributes, self.charset_name, self.charset_bom_marked, self.checksum, self.documents)

    source_path: string

    def with_source_path(self, source_path: string) -> Documents:
        return self if source_path is self.source_path else Documents(self.id, self.markers, source_path, self.file_attributes, self.charset_name, self.charset_bom_marked, self.checksum, self.documents)

    file_attributes: Optional[FileAttributes]

    def with_file_attributes(self, file_attributes: Optional[FileAttributes]) -> Documents:
        return self if file_attributes is self.file_attributes else Documents(self.id, self.markers, self.source_path, file_attributes, self.charset_name, self.charset_bom_marked, self.checksum, self.documents)

    charset_name: Optional[string]

    def with_charset_name(self, charset_name: Optional[string]) -> Documents:
        return self if charset_name is self.charset_name else Documents(self.id, self.markers, self.source_path, self.file_attributes, charset_name, self.charset_bom_marked, self.checksum, self.documents)

    charset_bom_marked: bool

    def with_charset_bom_marked(self, charset_bom_marked: bool) -> Documents:
        return self if charset_bom_marked is self.charset_bom_marked else Documents(self.id, self.markers, self.source_path, self.file_attributes, self.charset_name, charset_bom_marked, self.checksum, self.documents)

    checksum: Optional[Checksum]

    def with_checksum(self, checksum: Optional[Checksum]) -> Documents:
        return self if checksum is self.checksum else Documents(self.id, self.markers, self.source_path, self.file_attributes, self.charset_name, self.charset_bom_marked, checksum, self.documents)

    documents: IList<Yaml.Document>

    def with_documents(self, documents: IList<Yaml.Document>) -> Documents:
        return self if documents is self.documents else Documents(self.id, self.markers, self.source_path, self.file_attributes, self.charset_name, self.charset_bom_marked, self.checksum, documents)

@dataclass(frozen=True, eq=False)
class Document(Yaml):
    def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
        return v.VisitDocument(this, p)

    id: Guid

    def with_id(self, id: Guid) -> Document:
        return self if id is self.id else Document(id, self.prefix, self.markers, self.explicit, self.block, self.end)

    prefix: string

    def with_prefix(self, prefix: string) -> Document:
        return self if prefix is self.prefix else Document(self.id, prefix, self.markers, self.explicit, self.block, self.end)

    markers: Markers

    def with_markers(self, markers: Markers) -> Document:
        return self if markers is self.markers else Document(self.id, self.prefix, markers, self.explicit, self.block, self.end)

    explicit: bool

    def with_explicit(self, explicit: bool) -> Document:
        return self if explicit is self.explicit else Document(self.id, self.prefix, self.markers, explicit, self.block, self.end)

    block: Yaml.Block

    def with_block(self, block: Yaml.Block) -> Document:
        return self if block is self.block else Document(self.id, self.prefix, self.markers, self.explicit, block, self.end)

    end: End

    def with_end(self, end: End) -> Document:
        return self if end is self.end else Document(self.id, self.prefix, self.markers, self.explicit, self.block, end)

    @dataclass(frozen=True, eq=False)
    class End(Yaml):
        def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
            return v.VisitDocumentEnd(this, p)

        id: Guid

        def with_id(self, id: Guid) -> End:
            return self if id is self.id else End(id, self.prefix, self.markers, self.explicit)

        prefix: string

        def with_prefix(self, prefix: string) -> End:
            return self if prefix is self.prefix else End(self.id, prefix, self.markers, self.explicit)

        markers: Markers

        def with_markers(self, markers: Markers) -> End:
            return self if markers is self.markers else End(self.id, self.prefix, markers, self.explicit)

        explicit: bool

        def with_explicit(self, explicit: bool) -> End:
            return self if explicit is self.explicit else End(self.id, self.prefix, self.markers, explicit)

@dataclass(frozen=True, eq=False)
class Scalar(Yaml.Block, YamlKey):
    def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
        return v.VisitScalar(this, p)

    id: Guid

    def with_id(self, id: Guid) -> Scalar:
        return self if id is self.id else Scalar(id, self.prefix, self.markers, self.style, self.anchor, self.value)

    prefix: string

    def with_prefix(self, prefix: string) -> Scalar:
        return self if prefix is self.prefix else Scalar(self.id, prefix, self.markers, self.style, self.anchor, self.value)

    markers: Markers

    def with_markers(self, markers: Markers) -> Scalar:
        return self if markers is self.markers else Scalar(self.id, self.prefix, markers, self.style, self.anchor, self.value)

    style: Style

    def with_style(self, style: Style) -> Scalar:
        return self if style is self.style else Scalar(self.id, self.prefix, self.markers, style, self.anchor, self.value)

    anchor: Optional[Yaml.Anchor]

    def with_anchor(self, anchor: Optional[Yaml.Anchor]) -> Scalar:
        return self if anchor is self.anchor else Scalar(self.id, self.prefix, self.markers, self.style, anchor, self.value)

    value: string

    def with_value(self, value: string) -> Scalar:
        return self if value is self.value else Scalar(self.id, self.prefix, self.markers, self.style, self.anchor, value)

    class Style(Enum):
        DOUBLE_QUOTED = 0
        SINGLE_QUOTED = 1
        LITERAL = 2
        FOLDED = 3
        PLAIN = 4

@dataclass(frozen=True, eq=False)
class Mapping(Yaml.Block):
    def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
        return v.VisitMapping(this, p)

    id: Guid

    def with_id(self, id: Guid) -> Mapping:
        return self if id is self.id else Mapping(id, self.markers, self.opening_brace_prefix, self.entries, self.closing_brace_prefix, self.anchor)

    markers: Markers

    def with_markers(self, markers: Markers) -> Mapping:
        return self if markers is self.markers else Mapping(self.id, markers, self.opening_brace_prefix, self.entries, self.closing_brace_prefix, self.anchor)

    opening_brace_prefix: Optional[string]

    def with_opening_brace_prefix(self, opening_brace_prefix: Optional[string]) -> Mapping:
        return self if opening_brace_prefix is self.opening_brace_prefix else Mapping(self.id, self.markers, opening_brace_prefix, self.entries, self.closing_brace_prefix, self.anchor)

    entries: IList<Entry>

    def with_entries(self, entries: IList<Entry>) -> Mapping:
        return self if entries is self.entries else Mapping(self.id, self.markers, self.opening_brace_prefix, entries, self.closing_brace_prefix, self.anchor)

    closing_brace_prefix: Optional[string]

    def with_closing_brace_prefix(self, closing_brace_prefix: Optional[string]) -> Mapping:
        return self if closing_brace_prefix is self.closing_brace_prefix else Mapping(self.id, self.markers, self.opening_brace_prefix, self.entries, closing_brace_prefix, self.anchor)

    anchor: Optional[Yaml.Anchor]

    def with_anchor(self, anchor: Optional[Yaml.Anchor]) -> Mapping:
        return self if anchor is self.anchor else Mapping(self.id, self.markers, self.opening_brace_prefix, self.entries, self.closing_brace_prefix, anchor)

    @dataclass(frozen=True, eq=False)
    class Entry(Yaml):
        def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
            return v.VisitMappingEntry(this, p)

        id: Guid

        def with_id(self, id: Guid) -> Entry:
            return self if id is self.id else Entry(id, self.prefix, self.markers, self.key, self.before_mapping_value_indicator, self.value)

        prefix: string

        def with_prefix(self, prefix: string) -> Entry:
            return self if prefix is self.prefix else Entry(self.id, prefix, self.markers, self.key, self.before_mapping_value_indicator, self.value)

        markers: Markers

        def with_markers(self, markers: Markers) -> Entry:
            return self if markers is self.markers else Entry(self.id, self.prefix, markers, self.key, self.before_mapping_value_indicator, self.value)

        key: YamlKey

        def with_key(self, key: YamlKey) -> Entry:
            return self if key is self.key else Entry(self.id, self.prefix, self.markers, key, self.before_mapping_value_indicator, self.value)

        before_mapping_value_indicator: string

        def with_before_mapping_value_indicator(self, before_mapping_value_indicator: string) -> Entry:
            return self if before_mapping_value_indicator is self.before_mapping_value_indicator else Entry(self.id, self.prefix, self.markers, self.key, before_mapping_value_indicator, self.value)

        value: Yaml.Block

        def with_value(self, value: Yaml.Block) -> Entry:
            return self if value is self.value else Entry(self.id, self.prefix, self.markers, self.key, self.before_mapping_value_indicator, value)

@dataclass(frozen=True, eq=False)
class Sequence(Yaml.Block):
    def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
        return v.VisitSequence(this, p)

    id: Guid

    def with_id(self, id: Guid) -> Sequence:
        return self if id is self.id else Sequence(id, self.markers, self.opening_bracket_prefix, self.entries, self.closing_bracket_prefix, self.anchor)

    markers: Markers

    def with_markers(self, markers: Markers) -> Sequence:
        return self if markers is self.markers else Sequence(self.id, markers, self.opening_bracket_prefix, self.entries, self.closing_bracket_prefix, self.anchor)

    opening_bracket_prefix: Optional[string]

    def with_opening_bracket_prefix(self, opening_bracket_prefix: Optional[string]) -> Sequence:
        return self if opening_bracket_prefix is self.opening_bracket_prefix else Sequence(self.id, self.markers, opening_bracket_prefix, self.entries, self.closing_bracket_prefix, self.anchor)

    entries: IList<Entry>

    def with_entries(self, entries: IList<Entry>) -> Sequence:
        return self if entries is self.entries else Sequence(self.id, self.markers, self.opening_bracket_prefix, entries, self.closing_bracket_prefix, self.anchor)

    closing_bracket_prefix: Optional[string]

    def with_closing_bracket_prefix(self, closing_bracket_prefix: Optional[string]) -> Sequence:
        return self if closing_bracket_prefix is self.closing_bracket_prefix else Sequence(self.id, self.markers, self.opening_bracket_prefix, self.entries, closing_bracket_prefix, self.anchor)

    anchor: Optional[Yaml.Anchor]

    def with_anchor(self, anchor: Optional[Yaml.Anchor]) -> Sequence:
        return self if anchor is self.anchor else Sequence(self.id, self.markers, self.opening_bracket_prefix, self.entries, self.closing_bracket_prefix, anchor)

    @dataclass(frozen=True, eq=False)
    class Entry(Yaml):
        def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
            return v.VisitSequenceEntry(this, p)

        id: Guid

        def with_id(self, id: Guid) -> Entry:
            return self if id is self.id else Entry(id, self.prefix, self.markers, self.block, self.dash, self.trailing_comma_prefix)

        prefix: string

        def with_prefix(self, prefix: string) -> Entry:
            return self if prefix is self.prefix else Entry(self.id, prefix, self.markers, self.block, self.dash, self.trailing_comma_prefix)

        markers: Markers

        def with_markers(self, markers: Markers) -> Entry:
            return self if markers is self.markers else Entry(self.id, self.prefix, markers, self.block, self.dash, self.trailing_comma_prefix)

        block: Yaml.Block

        def with_block(self, block: Yaml.Block) -> Entry:
            return self if block is self.block else Entry(self.id, self.prefix, self.markers, block, self.dash, self.trailing_comma_prefix)

        dash: bool

        def with_dash(self, dash: bool) -> Entry:
            return self if dash is self.dash else Entry(self.id, self.prefix, self.markers, self.block, dash, self.trailing_comma_prefix)

        trailing_comma_prefix: Optional[string]

        def with_trailing_comma_prefix(self, trailing_comma_prefix: Optional[string]) -> Entry:
            return self if trailing_comma_prefix is self.trailing_comma_prefix else Entry(self.id, self.prefix, self.markers, self.block, self.dash, trailing_comma_prefix)

@dataclass(frozen=True, eq=False)
class Alias(Yaml.Block, YamlKey):
    def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
        return v.VisitAlias(this, p)

    id: Guid

    def with_id(self, id: Guid) -> Alias:
        return self if id is self.id else Alias(id, self.prefix, self.markers, self.anchor)

    prefix: string

    def with_prefix(self, prefix: string) -> Alias:
        return self if prefix is self.prefix else Alias(self.id, prefix, self.markers, self.anchor)

    markers: Markers

    def with_markers(self, markers: Markers) -> Alias:
        return self if markers is self.markers else Alias(self.id, self.prefix, markers, self.anchor)

    anchor: Yaml.Anchor

    def with_anchor(self, anchor: Yaml.Anchor) -> Alias:
        return self if anchor is self.anchor else Alias(self.id, self.prefix, self.markers, anchor)

@dataclass(frozen=True, eq=False)
class Anchor(Yaml):
    def accept_yaml(v: YamlVisitor[P], p: P) -> Yaml:
        return v.VisitAnchor(this, p)

    id: Guid

    def with_id(self, id: Guid) -> Anchor:
        return self if id is self.id else Anchor(id, self.prefix, self.postfix, self.markers, self.key)

    prefix: string

    def with_prefix(self, prefix: string) -> Anchor:
        return self if prefix is self.prefix else Anchor(self.id, prefix, self.postfix, self.markers, self.key)

    postfix: string

    def with_postfix(self, postfix: string) -> Anchor:
        return self if postfix is self.postfix else Anchor(self.id, self.prefix, postfix, self.markers, self.key)

    markers: Markers

    def with_markers(self, markers: Markers) -> Anchor:
        return self if markers is self.markers else Anchor(self.id, self.prefix, self.postfix, markers, self.key)

    key: string

    def with_key(self, key: string) -> Anchor:
        return self if key is self.key else Anchor(self.id, self.prefix, self.postfix, self.markers, key)

@dataclass(frozen=True, eq=False)
class Block(Yaml):
        pass
