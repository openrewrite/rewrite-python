import ast
from typing import Optional

from pytype import config
from pytype.pytd.pytd import CallableType
from pytype.tools.annotate_ast.annotate_ast import AnnotateAstVisitor, PytypeError, infer_types

from ..java import JavaType


class PythonTypeMapping:
    __enabled = False

    def __init__(self, source: str):
        pytype_options = config.Options.create(python_version='3.12', check=False, precise_return=True, output_debug=False)
        try:
            self._source_with_types = infer_types(source, pytype_options) if self.__enabled else None
        except PytypeError:
            self._source_with_types = None

    def resolve_types(self, node):
        if self._source_with_types:
            type_visitor = AnnotateAstVisitor(self._source_with_types, ast)
            type_visitor.visit(node)

    def type(self, node) -> Optional[JavaType]:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return JavaType.Primitive.String
            elif isinstance(node.value, bool):
                return JavaType.Primitive.Boolean
            elif isinstance(node.value, int):
                return JavaType.Primitive.Int
            elif isinstance(node.value, float):
                return JavaType.Primitive.Double
            else:
                return JavaType.Primitive.None_
        elif isinstance(node, ast.Call):
            return self.method_invocation_type(node)
        elif self.__enabled and hasattr(node, 'resolved_type'):
            return self.__map_type(node.resolved_type, node)
        return None

    def method_invocation_type(self, node) -> Optional[JavaType.Method]:
        return self.__map_type(node.func.resolved_type, node) if self.__enabled else None

    def __map_type(self, type, node):
        if isinstance(type, CallableType):
            if isinstance(node, ast.Name):
                name = node.id
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                name = node.func.attr
            else:
                name = ''
            return JavaType.Method(_name=name)
