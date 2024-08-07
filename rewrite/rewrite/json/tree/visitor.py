from rewrite.core import TreeVisitor, SourceFile
from rewrite.core.visitor import P
from rewrite.json.tree.support_types import Space
from rewrite.json.tree.tree import Document, Array, Json


class JsonVisitor(TreeVisitor[Json, P]):
    def is_acceptable(self, source_file: SourceFile, p: P) -> bool:
        return isinstance(source_file, Document)

    def visit_array(self, array: Array, p: P) -> Json:
        array = array.with_prefix(self.visit_space(array.prefix, p))
        array = array.with_markers(self.visit_markers(array.markers, p))
        array = array.with_values([self.visit(v, p) for v in array.values])
        return array

    def visit_space(self, prefix: Space, p: P) -> Space:
        pass
