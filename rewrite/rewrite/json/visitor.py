from typing import cast, TypeVar

from rewrite.core import TreeVisitor
from rewrite.json.tree.tree import *

P = TypeVar('P')

class JsonVisitor(TreeVisitor[Json, P]):
    def is_acceptable(self, source_file: SourceFile, p: P) -> bool:
        return isinstance(source_file, Json)

    def visit_array(self, array: Array, p: P) -> Json:
        array = array.with_prefix(self.visit_space(array.prefix, p))
        array = array.with_markers(self.visit_markers(array.markers, p))
        array = array.padding.with_values([self.visit_right_padded(v, p, ) for v in array.padding.values])
        return array

    def visit_document(self, document: Document, p: P) -> Json:
        document = document.with_prefix(self.visit_space(document.prefix, p))
        document = document.with_markers(self.visit_markers(document.markers, p))
        document = document.with_value(self.visit_and_cast(document.value, JsonValue, p))
        document = document.with_eof(self.visit_space(document.eof, p))
        return document

    def visit_empty(self, empty: Empty, p: P) -> Json:
        empty = empty.with_prefix(self.visit_space(empty.prefix, p))
        empty = empty.with_markers(self.visit_markers(empty.markers, p))
        return empty

    def visit_identifier(self, identifier: Identifier, p: P) -> Json:
        identifier = identifier.with_prefix(self.visit_space(identifier.prefix, p))
        identifier = identifier.with_markers(self.visit_markers(identifier.markers, p))
        return identifier

    def visit_literal(self, literal: Literal, p: P) -> Json:
        literal = literal.with_prefix(self.visit_space(literal.prefix, p))
        literal = literal.with_markers(self.visit_markers(literal.markers, p))
        return literal

    def visit_member(self, member: Member, p: P) -> Json:
        member = member.with_prefix(self.visit_space(member.prefix, p))
        member = member.with_markers(self.visit_markers(member.markers, p))
        member = member.padding.with_key(self.visit_right_padded(member.padding.key, p))
        member = member.with_value(self.visit_and_cast(member.value, JsonValue, p))
        return member

    def visit_object(self, json_object: JsonObject, p: P) -> Json:
        json_object = json_object.with_prefix(self.visit_space(json_object.prefix, p))
        json_object = json_object.with_markers(self.visit_markers(json_object.markers, p))
        json_object = json_object.padding.with_members([self.visit_right_padded(v, p, ) for v in json_object.padding.members])
        return json_object

    def visit_right_padded(self, right: Optional[JsonRightPadded[T]], p: P) -> JsonRightPadded[T]:
        return extensions.visit_right_padded(self, right, p)

    def visit_space(self, space: Space, p: P) -> Space:
        return space
