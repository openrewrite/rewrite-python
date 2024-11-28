from typing import Optional

from rewrite import Recipe, Tree, Cursor
from rewrite.java import JavaSourceFile, MethodDeclaration, J, Space
from rewrite.python import PythonVisitor, SpacesStyle, IntelliJ
from rewrite.visitor import P, T


class AutoFormat(Recipe):
    def get_visitor(self):
        return AutoFormatVisitor()


class AutoFormatVisitor(PythonVisitor):
    def __init__(self, stop_after: Tree = None):
        self._stop_after = stop_after

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        self._cursor = parent if parent is not None else Cursor(None, Cursor.ROOT_VALUE)
        cu = tree if isinstance(tree, JavaSourceFile) else self._cursor.first_enclosing_or_throw(JavaSourceFile)

        tree = SpacesVisitor(cu.get_style(SpacesStyle) or IntelliJ.spaces(), self._stop_after).visit(tree, p, self._cursor.fork())
        return tree


class SpacesVisitor(PythonVisitor):
    def __init__(self, style: SpacesStyle, stop_after: Tree = None):
        self._style = style
        self._stop_after = stop_after

    def visit_method_declaration(self, method_declaration: MethodDeclaration, p: P) -> J:
        return method_declaration.padding.with_parameters(
            method_declaration.padding.parameters.with_before(Space.SINGLE_SPACE if self._style.beforeParentheses.method_parentheses else Space.EMPTY)
        )
