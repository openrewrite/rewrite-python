from __future__ import annotations

from typing import Optional, TypeVar, cast

from rewrite import Tree, P, Cursor
from rewrite.java import J, Space, Statement, JRightPadded, Block, ClassDeclaration, MethodDeclaration, Import
from rewrite.python import PythonVisitor, BlankLinesStyle, CompilationUnit, MultiImport
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
        statement = super().visit_statement(statement, p)

        parent_cursor = self.cursor.parent_tree_cursor()
        top_level = isinstance(parent_cursor.value, CompilationUnit)

        if isinstance(statement, (Import, MultiImport)):
            parent_cursor.put_message('prev_import', True)
            prev_import = False
        else:
            prev_import = parent_cursor.get_message('prev_import', False)
            if prev_import:
                parent_cursor.put_message('prev_import', False)

        if top_level:
            if statement == cast(CompilationUnit, parent_cursor.value).statements[0]:
                statement = statement.with_prefix(statement.prefix.with_whitespace(''))
            else:
                min_lines = max(self._style.minimum.around_top_level_classes_functions if isinstance(statement, (ClassDeclaration, MethodDeclaration)) else 0,
                                self._style.minimum.after_top_level_imports if prev_import else 0)
                statement = minimum_lines_for_tree(statement, min_lines)
        else:
            in_block = isinstance(parent_cursor.value, Block)
            in_class = in_block and isinstance(parent_cursor.parent_tree_cursor().value, ClassDeclaration)
            min_lines = 0
            if in_class:
                is_first = cast(Block, parent_cursor.value).statements[0] is statement
                if not is_first and isinstance(statement, MethodDeclaration):
                    min_lines = max(min_lines, self._style.minimum.around_method)
                elif not is_first and isinstance(statement, ClassDeclaration):
                    min_lines = max(min_lines, self._style.minimum.around_class)
            if prev_import:
                min_lines = max(min_lines, self._style.minimum.after_local_imports)
            statement = minimum_lines_for_tree(statement, min_lines)
        return statement

    def post_visit(self, tree: T, p: P) -> Optional[T]:
        if self._stop_after and tree == self._stop_after:
            self._stop = True
        return tree

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[T]:
        return tree if self._stop else super().visit(tree, p, parent)


def minimum_lines_for_right_padded(tree: JRightPadded[J2], min_lines) -> JRightPadded[J2]:
    return tree.with_element(minimum_lines_for_tree(tree.element, min_lines))


def minimum_lines_for_tree(tree: J, min_lines) -> J:
    if min_lines == 0:
        return tree
    return tree.with_prefix(minimum_lines_for_space(tree.prefix, min_lines))


def minimum_lines_for_space(prefix: Space, min_lines) -> Space:
    if min_lines == 0:
        return prefix
    if not prefix.comments or \
            '\n' in prefix.whitespace or \
            (prefix.comments[0].multiline and '\n' in prefix.comments[0].text):
        return prefix.with_whitespace(minimum_lines_for_string(prefix.whitespace, min_lines))

    # the first comment is a trailing comment on the previous line
    c0 = prefix.comments[0].with_suffix(minimum_lines_for_string(prefix.comments[0].suffix, min_lines))
    return prefix if c0 is prefix.comments[0] else prefix.with_comments([c0] + prefix.comments[1:])


def minimum_lines_for_string(whitespace, min_lines):
    if min_lines == 0:
        return whitespace

    min_whitespace = whitespace
    for _ in range(min_lines - get_new_line_count(whitespace) + 1):
        min_whitespace = '\n' + min_whitespace

    return min_whitespace


def get_new_line_count(whitespace):
    return whitespace.count('\n')
