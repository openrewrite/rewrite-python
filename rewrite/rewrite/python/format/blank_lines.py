from __future__ import annotations

from typing import Optional, TypeVar

from rewrite import Tree, P, Cursor
from rewrite.java import J, Space, Statement
from rewrite.python import PythonVisitor, BlankLinesStyle, CompilationUnit
from rewrite.visitor import T

J2 = TypeVar('J2', bound=J)


class BlankLinesVisitor(PythonVisitor):
    def __init__(self, style: BlankLinesStyle, stop_after: Tree = None):
        self._style = style
        self._stop_after = stop_after
        self._stop = False

    def visit_compilation_unit(self, compilation_unit: CompilationUnit, p: P) -> J:
        if not compilation_unit.prefix.comments:
            compilation_unit = compilation_unit.with_prefix(Space.EMPTY)
        return super().visit_compilation_unit(compilation_unit, p)

    def visit_statement(self, statement: Statement, p: P) -> J:
        statement = statement.with_prefix(Space.EMPTY)
        return super().visit_statement(statement, p)

    def post_visit(self, tree: T, p: P) -> Optional[T]:
        if self._stop_after and tree == self._stop_after:
            self._stop = True
        return tree

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        return tree if self._stop else super().visit(tree, p, parent)
