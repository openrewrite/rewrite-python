from typing import cast, TypeVar

from rewrite import TreeVisitor
from .tree import *

P = TypeVar('P')

# noinspection DuplicatedCode
class YamlVisitor(TreeVisitor[Yaml, P]):
    def is_acceptable(self, source_file: SourceFile, p: P) -> bool:
        return isinstance(source_file, Yaml)

    def visit_documents(self, documents: Documents, p: P) -> Yaml:
        documents = documents.with_markers(self.visit_markers(documents.markers, p))
        documents = documents.with_documents([self.visit_and_cast(v, Document, p) for v in documents.documents])
        return documents

    def visit_document(self, document: Document, p: P) -> Yaml:
        document = document.with_markers(self.visit_markers(document.markers, p))
        document = document.with_block(self.visit_and_cast(document.block, Block, p))
        document = document.with_end(self.visit_and_cast(document.end, Document.End, p))
        return document

    def visit_document_end(self, end: Document.End, p: P) -> Yaml:
        end = end.with_markers(self.visit_markers(end.markers, p))
        return end

    def visit_scalar(self, scalar: Scalar, p: P) -> Yaml:
        scalar = scalar.with_markers(self.visit_markers(scalar.markers, p))
        scalar = scalar.with_anchor(self.visit_and_cast(scalar.anchor, Anchor, p))
        return scalar

    def visit_mapping(self, mapping: Mapping, p: P) -> Yaml:
        mapping = mapping.with_markers(self.visit_markers(mapping.markers, p))
        mapping = mapping.with_entries([self.visit_and_cast(v, Mapping.Entry, p) for v in mapping.entries])
        mapping = mapping.with_anchor(self.visit_and_cast(mapping.anchor, Anchor, p))
        return mapping

    def visit_mapping_entry(self, entry: Mapping.Entry, p: P) -> Yaml:
        entry = entry.with_markers(self.visit_markers(entry.markers, p))
        entry = entry.with_key(self.visit_and_cast(entry.key, YamlKey, p))
        entry = entry.with_value(self.visit_and_cast(entry.value, Block, p))
        return entry

    def visit_sequence(self, sequence: Sequence, p: P) -> Yaml:
        sequence = sequence.with_markers(self.visit_markers(sequence.markers, p))
        sequence = sequence.with_entries([self.visit_and_cast(v, Sequence.Entry, p) for v in sequence.entries])
        sequence = sequence.with_anchor(self.visit_and_cast(sequence.anchor, Anchor, p))
        return sequence

    def visit_sequence_entry(self, entry: Sequence.Entry, p: P) -> Yaml:
        entry = entry.with_markers(self.visit_markers(entry.markers, p))
        entry = entry.with_block(self.visit_and_cast(entry.block, Block, p))
        return entry

    def visit_alias(self, alias: Alias, p: P) -> Yaml:
        alias = alias.with_markers(self.visit_markers(alias.markers, p))
        alias = alias.with_anchor(self.visit_and_cast(alias.anchor, Anchor, p))
        return alias

    def visit_anchor(self, anchor: Anchor, p: P) -> Yaml:
        anchor = anchor.with_markers(self.visit_markers(anchor.markers, p))
        return anchor
