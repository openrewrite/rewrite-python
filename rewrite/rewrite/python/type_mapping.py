import ast

from pytype import config
from pytype.tools.annotate_ast.annotate_ast import AnnotateAstVisitor, PytypeError, infer_types


class PythonTypeMapping:
    __enabled = False

    def __init__(self, source: str):
        pytype_options = config.Options.create(python_version='3.12', check=False, precise_return=True)
        try:
            self._source_with_types = infer_types(source, pytype_options) if self.__enabled else None
        except PytypeError:
            self._source_with_types = None

    def resolve_types(self, node):
        if self._source_with_types:
            type_visitor = AnnotateAstVisitor(self._source_with_types, ast)
            type_visitor.visit(node)

    def type(self, node):
        return None
