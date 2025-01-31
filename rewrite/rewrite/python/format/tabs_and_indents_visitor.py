from __future__ import annotations

import sys
import textwrap
from enum import Enum, auto
from typing import TypeVar, Optional, Union, cast, List

from rewrite import Tree, Cursor, list_map, PrintOutputCapture, RecipeRunException
from rewrite.java import J, Space, JRightPadded, JLeftPadded, JContainer, JavaSourceFile, \
    Block, Label, ArrayDimension, ClassDeclaration, Empty, MethodDeclaration, \
    Binary, MethodInvocation, FieldAccess, Identifier, Lambda, Comment, TrailingComma, Expression, NewArray, \
    Annotation, Literal, If
from rewrite.python import PythonVisitor, TabsAndIndentsStyle, PySpace, PyContainer, PyRightPadded, DictLiteral, \
    CollectionLiteral, ExpressionStatement, OtherStyle, IntelliJ, ComprehensionExpression, PyComment
from rewrite.visitor import P, T, TreeVisitor

J2 = TypeVar('J2', bound=J)


class TabsAndIndentsVisitor(PythonVisitor[P]):

    def __init__(self, style: TabsAndIndentsStyle, other: OtherStyle = IntelliJ.other(), stop_after: Optional[Tree] = None):
        self._stop_after = stop_after
        self._style = style
        self._other = other
        self._stop = False

    def visit(self, tree: Optional[Tree], p: P, parent: Optional[Cursor] = None) -> Optional[J]:
        if parent is not None:
            self._cursor = parent
            if tree is None:
                return cast(Optional[J], self.default_value(None, p))

            for c in parent.get_path_as_cursors():
                v = c.value
                space = None
                if isinstance(v, J):
                    space = v.prefix
                elif isinstance(v, JRightPadded):
                    space = v.after
                elif isinstance(v, JLeftPadded):
                    space = v.before
                elif isinstance(v, JContainer):
                    space = v.before

                if space is not None and '\n' in space.last_whitespace:
                    indent = self.find_indent(space)
                    if indent != 0:
                        c.put_message("last_indent", indent)

            for next_parent in parent.get_path():
                if isinstance(next_parent, J):
                    self.pre_visit(next_parent, p)
                    break

        return super().visit(tree, p)

    def pre_visit(self, tree: T, p: P) -> Optional[T]:
        if isinstance(tree, (JavaSourceFile, Label, ArrayDimension, ClassDeclaration)):
            self.cursor.put_message("indent_type", self.IndentType.ALIGN)
        elif isinstance(tree, (Block, If)):
            self.cursor.put_message("indent_type", self.IndentType.INDENT)
        elif isinstance(tree, (DictLiteral, CollectionLiteral, NewArray, ComprehensionExpression)):
            self.cursor.put_message("indent_type", self.IndentType.CONTINUATION_INDENT
            if self._other.use_continuation_indent.collections_and_comprehensions else self.IndentType.INDENT)
        elif isinstance(tree, Expression) and not isinstance(tree, ExpressionStatement):
            self.cursor.put_message("indent_type", self.IndentType.INDENT)

        return tree

    def post_visit(self, tree: T, p: P) -> Optional[T]:
        if self._stop_after and tree == self._stop_after:
            self._stop = True
        return tree

    def visit_space(self, space: Optional[Space], loc: Optional[Union[PySpace.Location, Space.Location]],
                    p: P) -> Space:
        if space is None:
            return space  # type: ignore

        self._cursor.put_message("last_location", loc)
        parent = self._cursor.parent
        align_to_annotation = False

        if parent is not None:
            if isinstance(parent.value, Annotation):
                parent.parent_or_throw.put_message("after_annotation", True)
            elif not any([isinstance(_, Annotation) for _ in parent.get_path()]):
                align_to_annotation = self.cursor.poll_nearest_message("after_annotation", False)

        if loc == Space.Location.METHOD_SELECT_SUFFIX:
            chained_indent = cast(int, self.cursor.parent_tree_cursor().get_message("chained_indent", None))
            if chained_indent is not None:
                self.cursor.parent_tree_cursor().put_message("last_indent", chained_indent)
                return self._indent_to(space, chained_indent, loc)

        indent = cast(int, self.cursor.get_nearest_message("last_indent")) or 0
        indent_type = self.cursor.parent_or_throw.get_nearest_message("indent_type") or self.IndentType.ALIGN

        if not space.comments and '\n' not in space.last_whitespace or parent is None:
            return space

        cursor_value = self._cursor.value

        # Block spaces are always aligned to their parent
        # The second condition ensure init blocks are ignored.
        # TODO: Second condition might be removed since it's not relevant for Python
        align_block_prefix_to_parent = loc is Space.Location.BLOCK_PREFIX and '\n' in space.whitespace and \
                                       (isinstance(cursor_value, Block) and not isinstance(
                                           self.cursor.parent_tree_cursor().value, Block))

        align_block_to_parent = loc in (
            Space.Location.NEW_ARRAY_INITIALIZER_SUFFIX,
            Space.Location.CATCH_PREFIX,
            Space.Location.TRY_FINALLY,
            Space.Location.ELSE_PREFIX,
        )

        if (loc == Space.Location.EXTENDS and "\n" in space.whitespace) or \
                Space.Location.EXTENDS == self.cursor.parent_or_throw.get_message("last_location", None):
            indent_type = self.IndentType.CONTINUATION_INDENT

        if align_block_prefix_to_parent or align_block_to_parent or align_to_annotation:
            indent_type = self.IndentType.ALIGN

        if indent_type == self.IndentType.INDENT:
            indent += self._style.indent_size
        elif indent_type == self.IndentType.CONTINUATION_INDENT:
            indent += self._style.continuation_indent

        s: Space = self._indent_to(space, indent, loc)
        if isinstance(cursor_value, J):
            self.cursor.put_message("last_indent", indent)
        elif loc == Space.Location.METHOD_SELECT_SUFFIX:
            self.cursor.parent_tree_cursor().put_message("last_indent", indent)

        return s

    @staticmethod
    def compute_first_parameter_offset(method: MethodDeclaration, first_arg: J, cursor: Cursor) -> int:
        # Clear any annotations to avoid them affecting the offset calculation
        method = method.with_leading_annotations([])
        class FirstArgPrinter(PrintOutputCapture[TreeVisitor]):
            def append(self, text: Optional[str] = None) -> PrintOutputCapture[P]:
                if self._context.cursor.value is first_arg:
                    raise RecipeRunException()
                return super().append(text)

        printer = method.printer(cursor)
        capture = FirstArgPrinter(printer)
        try:
            printer.visit(method, capture, cursor.parent_or_throw)
        except RecipeRunException:
            source = capture.get_out()
            def_idx = source.index("def")
            async_idx = source.find("async")
            start_idx = async_idx if async_idx != -1 and async_idx < def_idx else def_idx
            return len(source[start_idx:]) + len(first_arg.prefix.last_whitespace)

    def visit_right_padded(self, right: Optional[JRightPadded[T]],
                           loc: Union[PyRightPadded.Location, JRightPadded.Location], p: P) -> Optional[
        JRightPadded[T]]:

        if right is None:
            return None

        self.cursor = Cursor(self._cursor, right)

        indent: int = cast(int, self.cursor.get_nearest_message("last_indent")) or 0

        t: T = right.element
        after = right.after
        # TODO: Check if the visit_and_cast is really required here

        if isinstance(t, J):
            elem = t
            trailing_comma = right.markers.find_first(TrailingComma)
            if '\n' in right.after.last_whitespace or '\n' in elem.prefix.last_whitespace:
                if loc in (JRightPadded.Location.FOR_CONDITION,
                           JRightPadded.Location.FOR_UPDATE):
                    raise ValueError("This case should not be possible, should be safe for removal...")
                elif loc in (JRightPadded.Location.METHOD_DECLARATION_PARAMETER,
                             JRightPadded.Location.RECORD_STATE_VECTOR):
                    if isinstance(elem, Empty):
                        elem = elem.with_prefix(self._indent_to(elem.prefix, indent, loc.after_location))
                        after = right.after
                    else:
                        container: JContainer[J] = cast(JContainer[J], self.cursor.parent_or_throw.value)
                        elements: List[J] = container.elements
                        first_arg: J = elements[0]
                        last_arg: J = elements[-1]

                        # TODO: style.MethodDeclarationParameters doesn't exist for Python
                        # but should be self._style.method_declaration_parameters.align_when_multiple
                        if self._style.method_declaration_parameters.align_multiline_parameters:
                            method = self.cursor.first_enclosing(MethodDeclaration)
                            if method is not None:
                                if "\n" in first_arg.prefix.last_whitespace:
                                    if self._other.use_continuation_indent.method_declaration_parameters:
                                        align_to = indent + self._style.continuation_indent
                                    else:
                                        align_to = self._get_length_of_whitespace(first_arg.prefix.last_whitespace)
                                else:
                                    align_to = indent + self.compute_first_parameter_offset(method, first_arg,
                                                                                            self.cursor)
                                self.cursor.parent_or_throw.put_message("last_indent", align_to - self._style.continuation_indent)
                                elem = self.visit_and_cast(elem, J, p)
                                self.cursor.parent_or_throw.put_message("last_indent", indent)
                                after = self._indent_to(right.after, indent if t is last_arg else align_to, loc.after_location)
                            else:
                                after = right.after
                        else:
                            elem = self.visit_and_cast(elem, J, p)
                            after = self._indent_to(right.after,
                                                    indent if t is last_arg else self._style.continuation_indent,
                                                    loc.after_location)

                elif loc == JRightPadded.Location.METHOD_INVOCATION_ARGUMENT:
                    elem, after = self._visit_method_invocation_argument_j_type(elem, right, indent, loc, p)
                elif loc in (JRightPadded.Location.NEW_CLASS_ARGUMENTS,
                             JRightPadded.Location.ARRAY_INDEX,
                             JRightPadded.Location.PARENTHESES,
                             JRightPadded.Location.TYPE_PARAMETER):
                    elem = self.visit_and_cast(elem, J, p)
                    after = self._indent_to(right.after, indent, loc.after_location)
                elif loc in (PyRightPadded.Location.COLLECTION_LITERAL_ELEMENT, PyRightPadded.Location.DICT_LITERAL_ELEMENT):
                    elem = self.visit_and_cast(elem, J, p)
                    args = cast(JContainer[J], self.cursor.parent_or_throw.value)
                    if not trailing_comma and args.padding.elements[-1] is right:
                        self.cursor.parent_or_throw.put_message("indent_type", self.IndentType.ALIGN)
                    after = self.visit_space(right.after, loc.after_location, p)
                    if trailing_comma:
                        self.cursor.parent_or_throw.put_message("indent_type", self.IndentType.ALIGN)
                        trailing_comma = trailing_comma.with_suffix(self.visit_space(trailing_comma.suffix, loc.after_location, p))
                        right = right.with_markers(right.markers.compute_by_type(TrailingComma, lambda t: trailing_comma))
                elif loc == JRightPadded.Location.ANNOTATION_ARGUMENT:
                    raise NotImplementedError("Annotation argument not implemented")
                else:
                    elem = self.visit_and_cast(elem, J, p)
                    after = self.visit_space(right.after, loc.after_location, p)
            else:
                if loc in (JRightPadded.Location.NEW_CLASS_ARGUMENTS, JRightPadded.Location.METHOD_INVOCATION_ARGUMENT):
                    any_other_arg_on_own_line = False
                    if "\n" not in elem.prefix.last_whitespace:
                        args = cast(JContainer[J], self.cursor.parent_or_throw.value)
                        for arg in args.padding.elements:
                            if arg == self.cursor.value:
                                continue
                            if "\n" in arg.element.prefix.last_whitespace:
                                any_other_arg_on_own_line = True
                                break
                        if not any_other_arg_on_own_line:
                            elem = self.visit_and_cast(elem, J, p)
                            after = self._indent_to(right.after, indent, loc.after_location)

                    if not any_other_arg_on_own_line:
                        if not isinstance(elem, Binary):
                            if not isinstance(elem, MethodInvocation) or "\n" in elem.prefix.last_whitespace:
                                self.cursor.put_message("last_indent", indent + self._style.continuation_indent)
                            else:
                                method_invocation = elem
                                select = method_invocation.select
                                if isinstance(select, (FieldAccess, Identifier, MethodInvocation)):
                                    self.cursor.put_message("last_indent", indent + self._style.continuation_indent)

                        elem = self.visit_and_cast(elem, J, p)
                        after = self.visit_space(right.after, loc.after_location, p)
                else:
                    elem = self.visit_and_cast(elem, J, p)
                    after = self.visit_space(right.after, loc.after_location, p)

            t = cast(T, elem)
        else:
            after = self.visit_space(right.after, loc.after_location, p)

        self.cursor = self.cursor.parent  # type: ignore
        return right.with_after(after).with_element(t)

    def visit_container(self, container: Optional[JContainer[J2]],
                        loc: Union[PyContainer.Location, JContainer.Location], p: P) -> JContainer[J2]:
        if container is None:
            return container  # type: ignore

        self._cursor = Cursor(self._cursor, container)

        indent = cast(int, self.cursor.get_nearest_message("last_indent")) or 0
        if '\n' in container.before.last_whitespace:
            if loc in (JContainer.Location.TYPE_PARAMETERS,
                       JContainer.Location.IMPLEMENTS,
                       JContainer.Location.THROWS,
                       JContainer.Location.NEW_CLASS_ARGUMENTS,
                       JContainer.Location.METHOD_DECLARATION_PARAMETERS):
                before = self._indent_to(container.before, indent + self._style.continuation_indent,
                                         loc.before_location)
                self.cursor.put_message("indent_type", self.IndentType.ALIGN)
                self.cursor.put_message("last_indent", indent + self._style.continuation_indent)
            else:
                before = self.visit_space(container.before, loc.before_location, p)
            js = list_map(lambda t: self.visit_right_padded(t, loc.element_location, p), container.padding.elements)
        else:
            if loc == JContainer.Location.METHOD_DECLARATION_PARAMETERS:
                self.cursor.put_message("indent_type", self.IndentType.CONTINUATION_INDENT if self._other.use_continuation_indent.method_declaration_parameters else self.IndentType.INDENT)
            elif loc == JContainer.Location.METHOD_INVOCATION_ARGUMENTS:
                self.cursor.put_message("indent_type", self.IndentType.CONTINUATION_INDENT if self._other.use_continuation_indent.method_call_arguments else self.IndentType.INDENT)
            before = self.visit_space(container.before, loc.before_location, p)
            js = list_map(lambda t: self.visit_right_padded(t, loc.element_location, p), container.padding.elements)

        self._cursor = self._cursor.parent  # type: ignore

        if container.padding.elements is js and container.before is before:
            return container
        return JContainer(before, js, container.markers)

    @staticmethod
    def _is_doc_comment(expression_statement: ExpressionStatement, cursor: Cursor) -> bool:
        expr = expression_statement.expression
        return isinstance(expr, Literal) and isinstance(expr.value_source, str) and (
                (expr.value_source.startswith('"""') and expr.value_source.endswith('"""')) or
                (expr.value_source.startswith("'''") and expr.value_source.endswith("'''"))) and \
            cursor.first_enclosing(Block) is not None

    def visit_expression_statement(self, expression_statement: ExpressionStatement, p: P) -> J:
        if self._is_doc_comment(expression_statement, self.cursor):
            prefix_before = len(expression_statement.prefix.last_whitespace.split("\n")[-1])
            stm = cast(ExpressionStatement, super().visit_expression_statement(expression_statement, p))
            literal = cast(Literal, stm.expression)
            shift = len(stm.prefix.last_whitespace.split("\n")[-1]) - prefix_before
            return stm.with_expression(
                literal.with_value_source(textwrap.indent(str(literal.value_source), shift * " ")[shift:]))

        return super().visit_expression_statement(expression_statement, p)

    def _indent_to(self, space: Space, column: int, space_location: Optional[Union[PySpace.Location, Space.Location]]) -> Space:
        s = space
        whitespace = s.whitespace

        if space_location == Space.Location.COMPILATION_UNIT_PREFIX and whitespace:
            s = s.with_whitespace("")
        elif not s.comments and "\n" not in s.last_whitespace:
            return s

        if not s.comments:
            indent = self.find_indent(s)
            if indent != column:
                shift = column - indent
                s = s.with_whitespace(self._indent(whitespace, shift))
        else:
            def whitespace_indent(text: str) -> str:
                # TODO: Placeholder function, taken from java openrewrite.StringUtils
                indent: List[str] = []
                for c in text:
                    if c == '\n' or c == '\r':
                        return ''.join(indent)
                    elif c.isspace():
                        indent.append(c)
                    else:
                        return ''.join(indent)
                return ''.join(indent)

            # TODO: This is the java version, however the python version is probably different
            has_file_leading_comment = space.comments and (
                    (space_location == Space.Location.COMPILATION_UNIT_PREFIX) or (
                        space_location == Space.Location.BLOCK_END) or
                    (space_location == Space.Location.CLASS_DECLARATION_PREFIX and space.comments[0].multiline)
            )

            final_column = column + self._style.indent_size if space_location == Space.Location.BLOCK_END else column
            last_indent: str = space.whitespace[space.whitespace.rfind('\n') + 1:]
            indent = self._get_length_of_whitespace(whitespace_indent(last_indent))

            if indent != final_column or s.comments:
                if (has_file_leading_comment or ("\n" in whitespace)) and (
                        # Do not shift single-line comments at column 0.
                        not (s.comments and isinstance(s.comments[0], PyComment) and
                             not s.comments[0].multiline and self._get_length_of_whitespace(s.whitespace) == 0)):
                    shift = final_column - indent
                    s = s.with_whitespace(whitespace[:whitespace.rfind('\n') + 1] + self._indent(last_indent, shift))

                final_space = s
                last_comment_pos = len(s.comments) - 1

                def _process_comment(i: int, c: Comment) -> Comment:
                    if isinstance(c, PyComment) and not c.multiline:
                        # Do not shift single line comments at col 0.
                        if i != last_comment_pos and self._get_length_of_whitespace(c.suffix) == 0:
                            return c

                    prior_suffix = space.whitespace if i == 0 else final_space.comments[i - 1].suffix

                    if space_location == Space.Location.BLOCK_END and i != len(final_space.comments) - 1:
                        to_column = column + self._style.indent_size
                    else:
                        to_column = column

                    new_c = c
                    if "\n" in prior_suffix or has_file_leading_comment:
                        new_c = c

                    if '\n' in new_c.suffix:
                        suffix_indent = self._get_length_of_whitespace(new_c.suffix)
                        shift = to_column - suffix_indent
                        new_c = new_c.with_suffix(self._indent(new_c.suffix, shift))

                    return new_c

                s = s.with_comments(list_map(lambda i, c: _process_comment(c, i), s.comments))
        return s

    def _indent(self, whitespace: str, shift: int) -> str:
        return self._shift(whitespace, shift)

    def _shift(self, text: str, shift: int) -> str:
        tab_indent = self._style.tab_size
        if not self._style.use_tab_character:
            tab_indent = sys.maxsize

        if shift > 0:
            text += '\t' * (shift // tab_indent)
            text += ' ' * (shift % tab_indent)
        else:
            if self._style.use_tab_character:
                len_text = len(text) + (shift // tab_indent)
            else:
                len_text = len(text) + shift
            if len_text >= 0:
                text = text[:len_text]

        return text

    def find_indent(self, space: Space) -> int:
        return self._get_length_of_whitespace(space.indent)

    def _get_length_of_whitespace(self, whitespace: Optional[str]) -> int:
        if whitespace is None:
            return 0
        length = 0
        for c in whitespace:
            length += self._style.tab_size if c == '\t' else 1
            if c in ('\n', '\r'):
                length = 0
        return length

    def _visit_method_invocation_argument_j_type(self, elem: J, right: JRightPadded[T], indent: int, loc: Union[PyRightPadded.Location, JRightPadded.Location], p: P) -> tuple[J, Space]:
        if "\n" not in elem.prefix.last_whitespace and isinstance(elem, Lambda):
            body = elem.body
            if not isinstance(body, Binary):
                if "\n" not in body.prefix.last_whitespace:
                    self.cursor.parent_or_throw.put_message("last_indent", indent + self._style.continuation_indent)

        elem = self.visit_and_cast(elem, J, p)
        after = self._indent_to(right.after, indent, loc.after_location)
        if after.comments or "\n" in after.last_whitespace:
            parent = self.cursor.parent_tree_cursor()
            grandparent = parent.parent_tree_cursor()
            # propagate indentation up in the method chain hierarchy
            if isinstance(grandparent.value, MethodInvocation) and grandparent.value.select == parent.value:
                grandparent.put_message("last_indent", indent)
                grandparent.put_message("chained_indent", indent)
        return elem, after

    class IndentType(Enum):
        ALIGN = auto()
        INDENT = auto()
        CONTINUATION_INDENT = auto()
