from typing import Optional, cast, TypeVar, Union

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

    def visit_method_declaration(self, method_declaration: MethodDeclaration, p: P) -> J:
        md: MethodDeclaration = cast(MethodDeclaration, super().visit_method_declaration(method_declaration, p))
        return md.padding.with_parameters(
            md.padding.parameters.with_before(
                Space.SINGLE_SPACE if self._before_parentheses.method_declaration else Space.EMPTY
            )
        )

    def visit_method_invocation(self, method_invocation: MethodInvocation, p: P) -> J:
        m: MethodInvocation = cast(MethodInvocation, super().visit_method_invocation(method_invocation, p))
        m = m.padding.with_arguments(
            m.padding.arguments.with_before(
                Space.SINGLE_SPACE if self._style.before_parentheses.method_call else Space.EMPTY)
        )
        return m

    def visit_array_access(self, array_access: ArrayAccess, p: P) -> J:
        a: ArrayAccess = cast(ArrayAccess, super().visit_array_access(array_access, p))
        use_space_within_brackets = self._style.within.brackets
        index_padding = a.dimension.padding.index
        element_prefix = update_space(index_padding.element.prefix, use_space_within_brackets)
        index_after = update_space(index_padding.after, use_space_within_brackets)

        a = a.with_dimension(
            a.dimension.padding.with_index(
                index_padding.with_element(
                    index_padding.element.with_prefix(element_prefix)
                ).with_after(index_after)
            ).with_prefix(update_space(a.dimension.prefix, self._style.before_parentheses.left_bracket))
        )
        return a

    def space_before(self, j: J2, space_before: bool) -> J2:
        space: Space = cast(Space, j.prefix)
        if space.comments or '\\' in space.whitespace:
            # don't touch whitespaces with comments or continuation characters
            return j

        return j.with_prefix(Space.SINGLE_SPACE if space_before else Space.EMPTY)


def update_space(s: Space, have_space: bool) -> Space:
    if s.comments:
        return s

    if have_space and not_single_space(s.whitespace):
        return s.with_whitespace(" ")
    elif not have_space and only_spaces_and_not_empty(s.whitespace):
        return s.with_whitespace("")
    else:
        return s


def only_spaces(s: Optional[str]) -> bool:
    return s is not None and all(c in {' ', '\t'} for c in s)


def only_spaces_and_not_empty(s: Optional[str]) -> bool:
    return bool(s) and only_spaces(s)


def not_single_space(s: Optional[str]) -> bool:
    return s is not None and only_spaces(s) and s != " "
