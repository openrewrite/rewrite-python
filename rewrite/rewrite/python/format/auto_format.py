from typing import Optional, cast, TypeVar

from .blank_lines import BlankLinesVisitor
from .normalize_format import NormalizeFormatVisitor
from ..style import BlankLinesStyle, SpacesStyle, IntelliJ
from ..visitor import PythonVisitor
from ... import Recipe, Tree, Cursor
from ...java import JavaSourceFile, MethodDeclaration, J, Space
from ...visitor import P, T


class AutoFormat(Recipe):
    def get_visitor(self):
        return AutoFormatVisitor()


class AutoFormatVisitor(PythonVisitor):
    def __init__(self, stop_after: Tree = None):
        self._stop_after = stop_after

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        self._cursor = parent if parent is not None else Cursor(None, Cursor.ROOT_VALUE)
        cu = tree if isinstance(tree, JavaSourceFile) else self._cursor.first_enclosing_or_throw(JavaSourceFile)

        tree = NormalizeFormatVisitor(self._stop_after).visit(tree, p, self._cursor.fork())
        tree = BlankLinesVisitor(cu.get_style(BlankLinesStyle) or IntelliJ.blank_lines(), self._stop_after).visit(tree, p, self._cursor.fork())
        tree = SpacesVisitor(cu.get_style(SpacesStyle) or IntelliJ.spaces(), self._stop_after).visit(tree, p, self._cursor.fork())
        return tree


J2 = TypeVar('J2', bound=J)


class SpacesVisitor(PythonVisitor):
    def __init__(self, style: SpacesStyle, stop_after: Tree = None):
        self._style = style
        self._before_parentheses = style.before_parentheses
        self._stop_after = stop_after

    def visit_method_declaration(self, md: MethodDeclaration, p: P) -> J:
        md: MethodDeclaration = cast(MethodDeclaration, super().visit_method_declaration(md, p))
        return md.padding.with_parameters(
            md.padding.parameters.with_before(
                Space.SINGLE_SPACE if self._before_parentheses.method_declaration else Space.EMPTY
            )
        )

    def space_before(self, j: J2, space_before: bool) -> J2:
        space: Space = cast(Space, j.prefix)
        if space.comments or '\\' in space.whitespace:
            # don't touch whitespaces with comments or continuation characters
            return j

        return j.with_prefix(Space.SINGLE_SPACE if space_before else Space.EMPTY)
