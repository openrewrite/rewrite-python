from typing import Optional, List, cast
from typing import Union, Callable

from rewrite.java import JavaVisitor, Space, JContainer, J, MethodDeclaration, \
    OmitParentheses, Try, JRightPadded, JLeftPadded, VariableDeclarations, Unary, Throw, Ternary, Switch, \
    ControlParentheses, ParameterizedType, ArrayDimension, NewArray, Modifier, MethodInvocation, Literal, \
    Lambda, Import, If, Identifier, ForEachLoop, \
    ClassDeclaration, Case, Block, \
    AssignmentOperation, Assignment, Assert, Annotation, Statement, Loop, Empty, Semicolon, TrailingComma, Yield, \
    WhileLoop, Return, Parentheses, FieldAccess, Continue, \
    Break, Comment, TextComment
from rewrite.java import tree as j
from ..visitor import T
from . import *
from .support_types import P, Py, PyRightPadded, PySpace, PyLeftPadded, PyContainer, J2
from .. import PrintOutputCapture, Cursor, Markers, Tree, Marker
from .visitor import PythonVisitor

JAVA_MARKER_WRAPPER: Callable[[str], str] = lambda out: f"/*~~{out}{'~~' if out else ''}>*/"""


class PythonPrinter(PythonVisitor[PrintOutputCapture[P]]):
    def __init__(self):
        super().__init__()
        self.delegate = PythonJavaPrinter(self)

    def visit(self, tree: Optional[T], p: PrintOutputCapture[P], parent: Optional[Cursor] = None) -> Optional[J]:
        if tree is None:
            return cast(Optional[J], self.default_value(None, p))
        if not isinstance(tree, Py):
            return self.delegate.visit(tree, p, parent)
        else:
            return super().visit(tree, p, parent)

    @PythonVisitor.cursor.setter
    def cursor(self, cursor: Cursor) -> None:
        self.delegate._cursor = cursor
        self._cursor = cursor

    def visit_async(self, async_: Async, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(async_, PySpace.Location.ASYNC_PREFIX, p)
        p.append("async")
        self.visit(async_.statement, p)
        return async_

    def visit_await(self, await_: Await, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(await_, PySpace.Location.AWAIT_PREFIX, p)
        p.append("await")
        self.visit(await_.expression, p)
        return await_

    def visit_python_binary(self, binary: Binary, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(binary, PySpace.Location.BINARY_PREFIX, p)
        self.visit(binary.left, p)
        self.visit_space(binary.padding.operator.before, PySpace.Location.BINARY_OPERATOR, p)

        if binary.operator == Binary.Type.NotIn:
            p.append("not")
            if binary.negation is not None:
                self.visit_space(binary.negation, PySpace.Location.BINARY_NEGATION, p)
            else:
                p.append(' ')
            p.append("in")
        elif binary.operator == Binary.Type.In:
            p.append("in")
        elif binary.operator == Binary.Type.Is:
            p.append("is")
        elif binary.operator == Binary.Type.IsNot:
            p.append("is")
            if binary.negation is not None:
                self.visit_space(binary.negation, PySpace.Location.BINARY_NEGATION, p)
            else:
                p.append(' ')
            p.append("not")
        elif binary.operator == Binary.Type.FloorDivision:
            p.append("//")
        elif binary.operator == Binary.Type.MatrixMultiplication:
            p.append("@")
        elif binary.operator == Binary.Type.Power:
            p.append("**")
        elif binary.operator == Binary.Type.StringConcatenation:
            pass  # empty
        else:
            raise ValueError(f"Unexpected binary operator: {binary.operator}")

        self.visit(binary.right, p)
        self.after_syntax(binary, p)
        return binary

    def visit_chained_assignment(self, chained_assignment: ChainedAssignment, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(chained_assignment, PySpace.Location.CHAINED_ASSIGNMENT_PREFIX, p)
        # TODO: Check name inconsistency between java and python CHAINED_ASSIGNMENT_VARIABLES vs CHAINED_ASSIGNMENT_VARIABLE
        self._print_right_padded(chained_assignment.padding.variables,
                                 PyRightPadded.Location.CHAINED_ASSIGNMENT_VARIABLES, "=", p)
        p.append('=')
        self.visit(chained_assignment.assignment, p)
        self.after_syntax(chained_assignment, p)
        return chained_assignment

    def visit_exception_type(self, exception_type: ExceptionType, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(exception_type, PySpace.Location.EXCEPTION_TYPE_PREFIX, p)
        if exception_type.exception_group:
            p.append("*")
        self.visit(exception_type.expression, p)
        return exception_type

    def visit_python_for_loop(self, for_loop: ForLoop, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(for_loop, PySpace.Location.FOR_LOOP_PREFIX, p)
        p.append("for")
        self.visit(for_loop.target, p)
        self._print_visit_left_padded("in", for_loop.padding.iterable, PyLeftPadded.Location.FOR_LOOP_ITERABLE, p)
        self.visit_right_padded(for_loop.padding.body, PyRightPadded.Location.FOR_LOOP_BODY, p)
        return for_loop

    def visit_literal_type(self, literal_type: LiteralType, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(literal_type, PySpace.Location.LITERAL_TYPE_PREFIX, p)
        self.visit(literal_type.literal, p)
        self.after_syntax(literal_type, p)
        return literal_type

    def visit_marker(self, marker: Marker, p: PrintOutputCapture[P]) -> Marker:
        if isinstance(marker, Semicolon):
            p.append(';')
        elif isinstance(marker, TrailingComma):
            p.append(',')
            self.visit_space(marker.suffix, Space.Location.ANY, p)
        return marker

    def visit_type_hint(self, type_hint: TypeHint, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(type_hint, PySpace.Location.TYPE_HINT_PREFIX, p)
        parent = self.cursor.parent_tree_cursor().value
        p.append("->" if isinstance(parent, MethodDeclaration) else ":")
        self.visit(type_hint.type_tree, p)
        self.after_syntax(type_hint, p)
        return type_hint

    def visit_compilation_unit(self, cu: CompilationUnit, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(cu, Space.Location.COMPILATION_UNIT_PREFIX, p)
        for import_ in cu.padding.imports:
            self.visit_right_padded(import_, PyRightPadded.Location.TOP_LEVEL_STATEMENT_SUFFIX, p)
        for statement in cu.padding.statements:
            self.visit_right_padded(statement, PyRightPadded.Location.TOP_LEVEL_STATEMENT_SUFFIX, p)

        self.visit_space(cu.eof, Space.Location.COMPILATION_UNIT_EOF, p)
        # TODO: The SuppressNewline marker used in the PythonPrinter does not exist?
        # if any(isinstance(marker, SuppressNewline) for marker in cu.markers.markers):
        #     out = p.get_out()
        #     if out and out[-1] == '\n':
        #         p._out[-1] = out[:-1]

        self.after_syntax(cu, p)
        return cu

    def visit_multi_import(self, multi_import: MultiImport, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(multi_import, PySpace.Location.MULTI_IMPORT_PREFIX, p)
        if multi_import.from_ is not None:
            p.append("from")
            self.visit_right_padded(multi_import.padding.from_, PyRightPadded.Location.MULTI_IMPORT_FROM, p)
        p.append("import")

        if multi_import.parenthesized:
            self._print_container("(", multi_import.padding.names, PyContainer.Location.MULTI_IMPORT_NAMES, ",",
                                          ")", p)
        else:
            self._print_container("", multi_import.padding.names, PyContainer.Location.MULTI_IMPORT_NAMES, ",",
                                          "", p)

        self.after_syntax(multi_import, p)
        return multi_import

    def visit_key_value(self, key_value: KeyValue, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(key_value, PySpace.Location.KEY_VALUE_PREFIX, p)
        self.visit_right_padded(key_value.padding.key, PyRightPadded.Location.KEY_VALUE_KEY_SUFFIX, p)
        p.append(':')
        self.visit(key_value.value, p)
        self.after_syntax(key_value, p)
        return key_value

    def visit_dict_literal(self, dict_literal: DictLiteral, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(dict_literal, PySpace.Location.DICT_LITERAL_PREFIX, p)
        self._print_container("{", dict_literal.padding.elements, PyContainer.Location.DICT_LITERAL_ELEMENTS,
                                      ",", "}",
                              p)
        self.after_syntax(dict_literal, p)
        return dict_literal

    def visit_collection_literal(self, collection_literal: CollectionLiteral, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(collection_literal, PySpace.Location.COLLECTION_LITERAL_PREFIX, p)
        elements = collection_literal.padding.elements

        if collection_literal.kind == CollectionLiteral.Kind.LIST:
            self._print_container("[", elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, ",", "]", p)
        elif collection_literal.kind == CollectionLiteral.Kind.SET:
            self._print_container("{", elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, ",", "}", p)
        elif collection_literal.kind == CollectionLiteral.Kind.TUPLE:
            if elements.markers.find_first(OmitParentheses) is not None:
                self._print_container("", elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, ",", "",
                                      p)
            else:
                self._print_container("(", elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, ",", ")",
                                      p)

        self.after_syntax(collection_literal, p)
        return collection_literal

    def visit_formatted_string(self, formatted_string: FormattedString, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(formatted_string, PySpace.Location.FORMATTED_STRING_PREFIX, p)
        p.append(formatted_string.delimiter)
        for part in formatted_string.parts:
            self.visit(part, p)
        if formatted_string.delimiter:
            idx = max(formatted_string.delimiter.find("'"), formatted_string.delimiter.find('"'))
            p.append(formatted_string.delimiter[idx:])
        return formatted_string

    def visit_formatted_string_value(self, value: FormattedString.Value, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(value, PySpace.Location.FORMATTED_STRING_VALUE_PREFIX, p)
        p.append('{')
        self.visit_right_padded(value.padding.expression, PyRightPadded.Location.FORMATTED_STRING_VALUE_EXPRESSION, p)

        if value.padding.debug is not None:
            p.append('=')
            self.visit_space(value.padding.debug.after, PySpace.Location.FORMATTED_STRING_VALUE_DEBUG_SUFFIX, p)

        if value.conversion is not None:
            p.append('!')
            if value.conversion == FormattedString.Value.Conversion.STR:
                p.append('s')
            elif value.conversion == FormattedString.Value.Conversion.REPR:
                p.append('r')
            elif value.conversion == FormattedString.Value.Conversion.ASCII:
                p.append('a')

        if value.format is not None:
            p.append(':')
            self.visit(value.format, p)

        p.append('}')
        return value

    def visit_pass(self, pass_: Pass, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(pass_, PySpace.Location.PASS_PREFIX, p)
        p.append("pass")
        self.after_syntax(pass_, p)
        return pass_

    def visit_trailing_else_wrapper(self, trailing_else_wrapper: TrailingElseWrapper, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(trailing_else_wrapper, PySpace.Location.TRAILING_ELSE_WRAPPER_PREFIX, p)
        self.visit(trailing_else_wrapper.statement, p)
        if not isinstance(trailing_else_wrapper.statement, Try):
            self.visit_space(
                trailing_else_wrapper.padding.else_block.before,
                Space.Location.ELSE_PREFIX,
                p
            )
            p.append("else")
            self.visit(trailing_else_wrapper.else_block, p)
        self.after_syntax(trailing_else_wrapper, p)
        return trailing_else_wrapper

    def visit_comprehension_expression(self, comprehension_expression: ComprehensionExpression,
                                       p: PrintOutputCapture[P]) -> J:
        self.before_syntax(comprehension_expression, PySpace.Location.COMPREHENSION_EXPRESSION_PREFIX, p)

        if comprehension_expression.kind in {ComprehensionExpression.Kind.DICT, ComprehensionExpression.Kind.SET}:
            open_, close = "{", "}"
        elif comprehension_expression.kind == ComprehensionExpression.Kind.LIST:
            open_, close = "[", "]"
        elif comprehension_expression.kind == ComprehensionExpression.Kind.GENERATOR:
            if comprehension_expression.markers.find_first(OmitParentheses) is not None:
                open_, close = "", ""
            else:
                open_, close = "(", ")"
        else:
            raise ValueError(f"Unexpected comprehension kind: {comprehension_expression.kind}")

        p.append(open_)
        self.visit(comprehension_expression.result, p)
        for clause in comprehension_expression.clauses:
            self.visit(clause, p)

        self.visit_space(comprehension_expression.suffix, PySpace.Location.COMPREHENSION_EXPRESSION_PREFIX, p)
        p.append(close)

        self.after_syntax(comprehension_expression, p)
        return comprehension_expression

    def visit_comprehension_condition(self, condition: ComprehensionExpression.Condition,
                                      p: PrintOutputCapture[P]) -> J:
        self.before_syntax(condition, PySpace.Location.COMPREHENSION_EXPRESSION_CONDITION_PREFIX, p)
        p.append("if")
        self.visit(condition.expression, p)
        return condition

    def visit_comprehension_clause(self, clause: ComprehensionExpression.Clause, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(clause, PySpace.Location.COMPREHENSION_EXPRESSION_CLAUSE_PREFIX, p)
        if clause.async_ and clause.padding.async_ is not None:
            p.append("async")
            self.visit_space(clause.padding.async_.after, PySpace.Location.COMPREHENSION_EXPRESSION_CLAUSE_ASYNC_SUFFIX,
                             p)
        p.append("for")
        self.visit(clause.iterator_variable, p)
        self.visit_space(clause.padding.iterated_list.before, PySpace.Location.COMPREHENSION_IN, p)
        p.append("in")
        self.visit(clause.iterated_list, p)
        if clause.conditions is not None:
            for condition in clause.conditions:
                self.visit(condition, p)
        return clause

    def visit_type_alias(self, type_alias: TypeAlias, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(type_alias, PySpace.Location.UNION_TYPE_PREFIX, p)
        p.append("type")
        self.visit(type_alias.name, p)
        self._print_visit_left_padded("=", type_alias.padding.value, PyLeftPadded.Location.TYPE_ALIAS_VALUE, p)
        self.after_syntax(type_alias, p)
        return type_alias

    def visit_yield_from(self, yield_from: YieldFrom, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(yield_from, PySpace.Location.YIELD_FROM_PREFIX, p)
        p.append("from")
        self.visit(yield_from.expression, p)
        return yield_from

    def visit_union_type(self, union_type: UnionType, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(union_type, PySpace.Location.UNION_TYPE_PREFIX, p)
        # TODO: Check name inconsistency between java and python UNION_TYPE_TYPES vs UNION_TYPE_TYPE
        self._print_right_padded(union_type.padding.types, PyRightPadded.Location.UNION_TYPE_TYPES, "|", p)
        self.after_syntax(union_type, p)
        return union_type

    def visit_variable_scope(self, variable_scope: VariableScope, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(variable_scope, PySpace.Location.VARIABLE_SCOPE_PREFIX, p)
        if VariableScope.Kind.GLOBAL == variable_scope.kind:
            p.append("global")
        elif VariableScope.Kind.NONLOCAL == variable_scope.kind:
            p.append("nonlocal")

        # TODO: Check name inconsistency between java and python VARIABLE_SCOPE_ELEMENTS vs VARIABLE_SCOPE_NAME_SUFFIX
        self._print_right_padded(variable_scope.padding.names, PyRightPadded.Location.VARIABLE_SCOPE_NAMES, ",",
                                 p)
        return variable_scope

    def visit_del(self, del_: Del, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(del_, PySpace.Location.DEL_PREFIX, p)
        p.append("del")
        # Note: PythonPrinter.java uses PyRightPadded.Location.DEL_ELEMENTS here but that doesn't exist in Python.
        # Instead we use PyRightPadded.Location.DEL_TARGETS as both actually point to PySpace.Location.DEL_TARGET_SUFFIX.
        self._print_right_padded(del_.padding.targets, PyRightPadded.Location.DEL_TARGETS, ",", p)
        return del_

    def visit_special_parameter(self, special_parameter: SpecialParameter, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(special_parameter, PySpace.Location.SPECIAL_PARAMETER_PREFIX, p)
        if special_parameter.kind == SpecialParameter.Kind.ARGS:
            p.append("*")
        elif special_parameter.kind == SpecialParameter.Kind.KWARGS:
            p.append("**")
        self.after_syntax(special_parameter, p)
        return special_parameter

    def visit_star(self, star: Star, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(star, PySpace.Location.STAR_PREFIX, p)
        if Star.Kind.LIST == star.kind:
            p.append('*')
        elif Star.Kind.DICT == star.kind:
            p.append('**')
        self.visit(star.expression, p)
        self.after_syntax(star, p)
        return star

    def visit_named_argument(self, named_argument: NamedArgument, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(named_argument, PySpace.Location.NAMED_ARGUMENT, p)
        self.visit(named_argument.name, p)
        self._print_visit_left_padded("=", named_argument.padding.value, PyLeftPadded.Location.NAMED_ARGUMENT_VALUE,
                                      p)
        return named_argument

    def visit_type_hinted_expression(self, type_hinted_expression: TypeHintedExpression, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(type_hinted_expression, PySpace.Location.TYPE_HINTED_EXPRESSION_PREFIX, p)
        self.visit(type_hinted_expression.expression, p)
        self.visit(type_hinted_expression.type_hint, p)
        self.after_syntax(type_hinted_expression, p)
        return type_hinted_expression

    def visit_error_from(self, error_from: ErrorFrom, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(error_from, PySpace.Location.ERROR_FROM_PREFIX, p)
        self.visit(error_from.error, p)
        # TODO: Check name inconsistency between java and python ERROR_FROM_SOURCE vs ERROR_FROM_PREFIX?
        self.visit_space(error_from.padding.from_.before, PySpace.Location.ERROR_FROM_PREFIX, p)
        p.append("from")
        self.visit(error_from.from_, p)
        return error_from

    def visit_match_case(self, match_case: MatchCase, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(match_case, PySpace.Location.MATCH_CASE_PREFIX, p)
        self.visit(match_case.pattern, p)
        if match_case.padding.guard is not None:
            self.visit_space(match_case.padding.guard.before, PySpace.Location.MATCH_CASE_GUARD, p)
            p.append("if")
            self.visit(match_case.guard, p)
        return match_case

    def visit_match_case_pattern(self, pattern: MatchCase.Pattern, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(pattern, PySpace.Location.MATCH_PATTERN_PREFIX, p)
        children = pattern.padding.children
        if pattern.kind == MatchCase.Pattern.Kind.AS:
            self._print_container("", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, "as", "", p)
        elif pattern.kind in {MatchCase.Pattern.Kind.CAPTURE, MatchCase.Pattern.Kind.LITERAL}:
            self.visit_container(children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, p)
        elif pattern.kind == MatchCase.Pattern.Kind.CLASS:
            self.visit_space(children.before, PySpace.Location.MATCH_CASE_PATTERN_PREFIX, p)
            self.visit_right_padded(children.padding.elements[0], PyRightPadded.Location.MATCH_CASE_PATTERN_CHILD, p)
            self._print_container("(", JContainer(Space.EMPTY, children.padding.elements[1:], Markers.EMPTY),
                                  PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, ",", ")", p)
        elif pattern.kind == MatchCase.Pattern.Kind.DOUBLE_STAR:
            self._print_container("**", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, "", "", p)
        elif pattern.kind == MatchCase.Pattern.Kind.KEY_VALUE:
            self._print_container("", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, ":", "", p)
        elif pattern.kind == MatchCase.Pattern.Kind.KEYWORD:
            self._print_container("", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, "=", "", p)
        elif pattern.kind == MatchCase.Pattern.Kind.MAPPING:
            self._print_container("{", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, ",", "}", p)
        elif pattern.kind == MatchCase.Pattern.Kind.OR:
            self._print_container("", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, "|", "", p)
        elif pattern.kind == MatchCase.Pattern.Kind.SEQUENCE:
            self._print_container("", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, ",", "", p)
        elif pattern.kind == MatchCase.Pattern.Kind.SEQUENCE_LIST:
            self._print_container("[", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, ",", "]", p)
        elif pattern.kind in {MatchCase.Pattern.Kind.GROUP, MatchCase.Pattern.Kind.SEQUENCE_TUPLE}:
            self._print_container("(", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, ",", ")", p)
        elif pattern.kind == MatchCase.Pattern.Kind.STAR:
            self._print_container("*", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, "", "", p)
        elif pattern.kind == MatchCase.Pattern.Kind.VALUE:
            self._print_container("", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, "", "", p)
        elif pattern.kind == MatchCase.Pattern.Kind.WILDCARD:
            self._print_container("_", children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, "", "", p)

        return pattern

    def visit_slice(self, slice_: Slice, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(slice_, PySpace.Location.SLICE_PREFIX, p)
        self.visit_right_padded(slice_.padding.start, PyRightPadded.Location.SLICE_START, p)
        p.append(':')
        if slice_.padding.stop is not None:
            self.visit_right_padded(slice_.padding.stop, PyRightPadded.Location.SLICE_STOP, p)
            if slice_.padding.step is not None:
                p.append(':')
                self.visit_right_padded(slice_.padding.step, PyRightPadded.Location.SLICE_STEP, p)
        return slice_

    # CUSTOM VISIT METHODS FOR VISIT CONTAINER, VISIT SPACE, VISIT RIGHT PADDED, VISIT LEFT PADDED
    def _print_container(self, before: str, container: Optional[JContainer[J2]],
                         loc: PyContainer.Location, suffix_between: str, after: str,
                         p: PrintOutputCapture[P]) -> None:
        if container is None:
            return None
        self.visit_space(container.before, loc.before_location, p)
        p.append(before)
        self._print_right_padded(container.padding.elements, loc.element_location, suffix_between, p)
        p.append("" if after is None else after)

    def _print_right_padded(self, nodes: List[JRightPadded[J2]], location: PyRightPadded.Location,
                            suffix_between: str, p: PrintOutputCapture[P]) -> None:
        for i, node in enumerate(nodes):
            self.visit(node.element, p)
            self.visit_space(node.after, location.after_location, p)
            self.visit_markers(node.markers, p)
            if i < len(nodes) - 1:
                p.append(suffix_between)

    def _print_visit_left_padded(self, s: str, left: JLeftPadded[J2], _: PyLeftPadded.Location,
                                 p: PrintOutputCapture[P]) -> None:
        self.delegate.visit_space(left.before, Space.Location.LANGUAGE_EXTENSION, p)
        p.append(s)
        self.cursor = Cursor(self.cursor, left)
        t = left.element
        if isinstance(t, J):
            self.visit_and_cast(left.element, J, p)

        self.cursor = self.cursor.parent  # pyright: ignore [reportAttributeAccessIssue]
        self.visit_markers(left.markers, p)

    def visit_container(self, container: Optional[JContainer[J2]],
                        loc: Union[PyContainer.Location, JContainer.Location], p: PrintOutputCapture[P]) -> JContainer[
        # pyright: ignore
        J2]:
        raise NotImplementedError("Should not be triggered")

    def visit_space(self, space: Optional[Space], loc: Optional[Union[PySpace.Location, Space.Location]],
                    p: PrintOutputCapture[P]) -> Space:
        loc_ = Space.Location.LANGUAGE_EXTENSION if isinstance(loc, PySpace.Location) else loc
        return self.delegate.visit_space(space, loc_, p)  # pyright: ignore [reportArgumentType]

    def before_syntax(
            self,
            py: Py,
            loc: Union[Space.Location, PySpace.Location],
            p: PrintOutputCapture[P],
    ) -> None:
        """
        Unified before_syntax method that handles all cases from Java overloads.
        1. before_syntax(py: Py, loc: Location, p: PrintOutputCapture)
        2. before_syntax(py: Py, loc: PySpace.Location, p: PrintOutputCapture)
        """
        return self._before_syntax_internal(py.prefix, py.markers, loc, p)

    def _before_syntax_internal(
            self,
            prefix: Space,
            markers: Markers,
            loc: Optional[Union[Space.Location, PySpace.Location]],
            p: PrintOutputCapture
    ) -> None:
        """
        Implementation of the common before_syntax logic
        """
        for marker in markers.markers:
            p.append(p.marker_printer.before_prefix(
                marker,
                Cursor(self.cursor, marker),
                JAVA_MARKER_WRAPPER
            ))

        if loc is not None:
            self.visit_space(prefix, loc, p)

        self.visit_markers(markers, p)

        for marker in markers.markers:
            p.append(p.marker_printer.before_syntax(
                marker,
                Cursor(self.cursor, marker),
                JAVA_MARKER_WRAPPER
            ))

    def after_syntax(
            self,
            arg: Union[Py, Markers],
            p: PrintOutputCapture
    ) -> None:
        """
        Unified after_syntax method that handles both cases from Java overloads.
        Usage patterns:
        1. after_syntax(py: Py, p: PrintOutputCapture)
        2. after_syntax(markers: Markers, p: PrintOutputCapture)
        """
        markers = arg.markers if isinstance(arg, Py) else arg

        for marker in markers.markers:
            p.append(p.marker_printer.after_syntax(
                marker,
                Cursor(self.cursor, marker),
                JAVA_MARKER_WRAPPER
            ))


class JavaPrinter(JavaVisitor[PrintOutputCapture[P]]):

    def before_syntax(self,
                      j_or_prefix: Union[J, Space],
                      loc: Optional[Space.Location],
                      p: PrintOutputCapture[P],
                      markers: Markers = Markers.EMPTY) -> None:
        # If j_or_prefix is a J type, extract prefix and markers
        if isinstance(j_or_prefix, J):
            self.before_syntax(j_or_prefix.prefix, loc, p, j_or_prefix.markers)
        else:
            markers_list = markers.markers

            # Process markers before prefix
            for marker in markers_list:
                p.append(p.marker_printer.before_prefix(
                    marker,
                    Cursor(self.cursor, marker),
                    JAVA_MARKER_WRAPPER
                ))

            if loc is not None:
                self.visit_space(j_or_prefix, loc, p)
            self.visit_markers(markers, p)
            for marker in markers_list:
                p.append(p.marker_printer.before_syntax(
                    marker,
                    Cursor(self.cursor, marker),
                    JAVA_MARKER_WRAPPER
                ))

    def after_syntax(self, j_or_markers: Union[J, Markers], p: PrintOutputCapture[P]) -> None:
        # If j_or_markers is a J type, extract markers and call after_syntax
        markers = j_or_markers.markers if isinstance(j_or_markers, J) else j_or_markers

        markers_list = markers.markers
        for marker in markers_list:
            p.append(p.marker_printer.after_syntax(
                marker,
                Cursor(self.cursor, marker),
                JAVA_MARKER_WRAPPER
            ))

    def visit_statements(self, statements: List[JRightPadded[Statement]], location: JRightPadded.Location,
                         p: PrintOutputCapture[P]) -> None:
        for padded_stat in statements:
            self._print_statement(padded_stat, location, p)

    def _print_statement(self, padded_stat: Optional[JRightPadded[Statement]], location: JRightPadded.Location,
                         p: PrintOutputCapture[P]) -> None:
        if padded_stat is None:
            return

        self.visit(padded_stat.element, p)
        self.visit_space(padded_stat.after, location.after_location, p)
        self.visit_markers(padded_stat.markers, p)

    def _print_container(self, before: str, container: Optional[JContainer[J2]], location: JContainer.Location,
                         suffix_between: str, after: Optional[str], p: PrintOutputCapture[P]) -> None:
        if container is None:
            return
        self.before_syntax(container.before, location.before_location, p, markers=container.markers)
        p.append(before)
        self._print_right_padded_list(container.padding.elements, location.element_location, suffix_between, p)
        self.after_syntax(container.markers, p)
        p.append("" if after is None else after)

    def _print_right_padded_list(self, nodes: List[JRightPadded[J2]], location: JRightPadded.Location,
                                 suffix_between: str,
                                 p: PrintOutputCapture[P]) -> None:
        for i, node in enumerate(nodes):
            self.visit(node.element, p)
            self.visit_space(node.after, location.after_location, p)
            self.visit_markers(node.markers, p)
            if i < len(nodes) - 1:
                p.append(suffix_between)

    def _print_right_padded(self, right_padded: Optional[JRightPadded[J2]], location: JRightPadded.Location,
                            suffix: Optional[str], p: PrintOutputCapture[P]) -> None:
        if right_padded is not None:
            self.before_syntax(Space.EMPTY, None, p, right_padded.markers)
            self.visit(right_padded.element, p)
            self.after_syntax(right_padded.markers, p)
            self.visit_space(right_padded.after, location.after_location, p)
            if suffix is not None:
                p.append(suffix)

    def _print_left_padded(self, prefix: Optional[str], left_padded: Optional[JLeftPadded[J2]],
                           location: JLeftPadded.Location, p: PrintOutputCapture[P]) -> None:
        if left_padded is not None:
            self.before_syntax(left_padded.before, location.before_location, p, left_padded.markers)
            if prefix is not None:
                p.append(prefix)
            self.visit(left_padded.element, p)
            self.after_syntax(left_padded.markers, p)

    def visit_space(self, space: Space, _: Optional[Space.Location], p: PrintOutputCapture[P]) -> Space:
        p.append(space.whitespace)
        comments = space.comments
        for comment in comments:
            self.visit_markers(comment.markers, p)
            self.print_comment(comment, p)
            p.append(comment.suffix)
        return space

    @staticmethod
    def print_comment(comment: Comment, p: PrintOutputCapture[P]):
        if isinstance(comment, PyComment):
            p.append("#").append(comment.text)
        elif isinstance(comment, TextComment):
            raise NotImplementedError("TextComment not yet supported")
        else:
            raise ValueError(f"Unexpected comment type: {type(comment)}")

    def visit_field_access(self, field_access: FieldAccess, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(field_access, Space.Location.FIELD_ACCESS_PREFIX, p)
        self.visit(field_access.target, p)
        self._print_left_padded(".", field_access.padding.name, JLeftPadded.Location.FIELD_ACCESS_NAME, p)
        self.after_syntax(field_access, p)
        return field_access

    def visit_parentheses(self, parens: Parentheses[J2], p: PrintOutputCapture[P]) -> J:
        self.before_syntax(parens, Space.Location.PARENTHESES_PREFIX, p)
        p.append('(')
        self._print_right_padded(parens.padding.tree, JRightPadded.Location.PARENTHESES, ")", p)
        self.after_syntax(parens, p)
        return parens

    def visit_while_loop(self, while_loop: WhileLoop, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(while_loop, Space.Location.WHILE_PREFIX, p)
        p.append("while")
        self.visit(while_loop.condition, p)
        self._print_statement(while_loop.padding.body, JRightPadded.Location.WHILE_BODY, p)
        self.after_syntax(while_loop, p)
        return while_loop

    def visit_continue(self, continue_: Continue, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(continue_, Space.Location.CONTINUE_PREFIX, p)
        p.append("continue")
        self.visit(continue_.label, p)
        self.after_syntax(continue_, p)
        return continue_

    def visit_empty(self, empty: Empty, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(empty, Space.Location.EMPTY_PREFIX, p)
        self.after_syntax(empty, p)
        return empty

    def visit_return(self, return_: Return, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(return_, Space.Location.RETURN_PREFIX, p)
        p.append("return")
        self.visit(return_.expression, p)
        self.after_syntax(return_, p)
        return return_

    def visit_yield(self, yield_: Yield, p: PrintOutputCapture[P]) -> Yield:
        self.before_syntax(yield_, Space.Location.YIELD_PREFIX, p)
        if not yield_.implicit:
            p.append("yield")
        self.visit(yield_.value, p)
        self.after_syntax(yield_, p)
        return yield_

    def visit_break(self, break_: Break, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(break_, Space.Location.BREAK_PREFIX, p)
        p.append("break")
        self.visit(break_.label, p)
        self.after_syntax(break_, p)
        return break_

    def visit_left_padded(self, left: Optional[JLeftPadded[T]], loc: JLeftPadded.Location, p: PrintOutputCapture[P]) -> \
            Optional[
        JLeftPadded[T]]:
        return super().visit_left_padded(left, loc, p)

    def visit_right_padded(self, right: Optional[JRightPadded[T]], loc: JRightPadded.Location,
                           p: PrintOutputCapture[P]) -> Optional[
        JRightPadded[T]]:
        return super().visit_right_padded(right, loc, p)


class PythonJavaPrinter(JavaPrinter):
    delegate: PythonPrinter

    def __init__(self, delegate: PythonPrinter):
        self.delegate = delegate

    def visit(self, tree: Union[Optional[Tree], List[J2]], p: PrintOutputCapture[P],
              parent: Optional[Cursor] = None) -> Optional[J]:
        if tree is None:
            return cast(Optional[J], self.default_value(None, p))

        if isinstance(tree, list):
            for t in tree:
                if isinstance(t, Py):
                    self.delegate.visit(t, p)
                else:
                    super().visit(t, p, parent)
        else:
            if isinstance(tree, Py):
                return self.delegate.visit(tree, p)
            else:
                return super().visit(tree, p, parent)

    @property
    def cursor(self) -> Cursor:
        return super().cursor

    @cursor.setter
    def cursor(self, cursor: Cursor) -> None:
        self.delegate._cursor = cursor
        self._cursor = cursor

    def visit_annotation(self, annotation: Annotation, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(annotation, Space.Location.ANNOTATION_PREFIX, p)
        p.append("@")
        self.visit(annotation.annotation_type, p)
        self._print_container("(", annotation.padding.arguments,
                              JContainer.Location.ANNOTATION_ARGUMENTS, ",", ")", p)
        self.after_syntax(annotation, p)
        return annotation

    def visit_array_dimension(self, array_dimension: ArrayDimension, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(array_dimension, Space.Location.DIMENSION_PREFIX, p)
        p.append("[")
        self._print_right_padded(array_dimension.padding.index,
                                 JRightPadded.Location.ARRAY_INDEX, "]", p)
        self.after_syntax(array_dimension, p)
        return array_dimension

    def visit_assert(self, assert_: Assert, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(assert_, Space.Location.ASSERT_PREFIX, p)
        p.append("assert")
        self.visit(assert_.condition, p)
        if assert_.detail is not None:
            self._print_left_padded(",", assert_.detail,
                                    JLeftPadded.Location.ASSERT_DETAIL, p)
        self.after_syntax(assert_, p)
        return assert_

    def visit_assignment(self, assignment: Assignment, p: PrintOutputCapture[P]) -> J:
        parent_tree = self.cursor.parent_tree_cursor().value

        symbol = "=" if (isinstance(parent_tree, (Block, CompilationUnit)) or
                         (isinstance(parent_tree, If) and parent_tree.then_part == assignment) or
                         (isinstance(parent_tree, If.Else) and parent_tree.body == assignment) or
                         (isinstance(parent_tree, Loop) and parent_tree.body == assignment)) else ":="

        self.before_syntax(assignment, Space.Location.ASSIGNMENT_PREFIX, p)
        self.visit(assignment.variable, p)
        self._print_left_padded(symbol, assignment.padding.assignment,
                                JLeftPadded.Location.ASSIGNMENT, p)
        self.after_syntax(assignment, p)
        return assignment

    def visit_assignment_operation(self, assign_op: AssignmentOperation, p: PrintOutputCapture[P]) -> J:
        operator_map = {
            AssignmentOperation.Type.Addition: '+=',
            AssignmentOperation.Type.Subtraction: '-=',
            AssignmentOperation.Type.Multiplication: '*=',
            AssignmentOperation.Type.Division: '/=',
            AssignmentOperation.Type.Modulo: '%=',
            AssignmentOperation.Type.BitAnd: '&=',
            AssignmentOperation.Type.BitOr: '|=',
            AssignmentOperation.Type.BitXor: '^=',
            AssignmentOperation.Type.LeftShift: '<<=',
            AssignmentOperation.Type.RightShift: '>>=',
            AssignmentOperation.Type.UnsignedRightShift: '>>>=',
            AssignmentOperation.Type.Exponentiation: '**=',
            AssignmentOperation.Type.FloorDivision: '//=',
            AssignmentOperation.Type.MatrixMultiplication: '@='
        }

        keyword = operator_map.get(assign_op.operator, None)
        if keyword is None:
            raise ValueError(f"Unknown assignment operator: {assign_op.operator}")

        self.before_syntax(assign_op, Space.Location.ASSIGNMENT_OPERATION_PREFIX, p)
        self.visit(assign_op.variable, p)
        self.visit_space(assign_op.padding.operator.before,
                         Space.Location.ASSIGNMENT_OPERATION_OPERATOR, p)
        p.append(keyword)
        self.visit(assign_op.assignment, p)
        self.after_syntax(assign_op, p)
        return assign_op


    def visit_binary(self, binary: j.Binary, p: PrintOutputCapture[P]) -> J:
        operator_map = {
            j.Binary.Type.Addition: '+',
            j.Binary.Type.Subtraction: '-',
            j.Binary.Type.Multiplication: '*',
            j.Binary.Type.Division: '/',
            j.Binary.Type.Modulo: '%',
            j.Binary.Type.LessThan: '<',
            j.Binary.Type.GreaterThan: '>',
            j.Binary.Type.LessThanOrEqual: '<=',
            j.Binary.Type.GreaterThanOrEqual: '>=',
            j.Binary.Type.Equal: '==',
            j.Binary.Type.NotEqual: '!=',
            j.Binary.Type.BitAnd: '&',
            j.Binary.Type.BitOr: '|',
            j.Binary.Type.BitXor: '^',
            j.Binary.Type.LeftShift: '<<',
            j.Binary.Type.RightShift: '>>',
            j.Binary.Type.UnsignedRightShift: '>>>',
            j.Binary.Type.Or: 'or',
            j.Binary.Type.And: 'and'
        }

        keyword = operator_map.get(binary.operator, None)
        if not keyword:
            raise ValueError(f"Unknown binary operator: {binary.operator}")

        self.before_syntax(binary, Space.Location.BINARY_PREFIX, p)
        self.visit(binary.left, p)
        self.visit_space(binary.padding.operator.before,
                         Space.Location.BINARY_OPERATOR, p)
        p.append(keyword)
        self.visit(binary.right, p)
        self.after_syntax(binary, p)
        return binary

    def visit_block(self, block: Block, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(block, Space.Location.BLOCK_PREFIX, p)
        p.append(':')
        self.visit_statements(block.padding.statements,
                              JRightPadded.Location.BLOCK_STATEMENT, p)
        self.visit_space(block.end, Space.Location.BLOCK_END, p)
        self.after_syntax(block, p)
        return block

    def visit_case(self, ca: Case, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(ca, Space.Location.CASE_PREFIX, p)
        elem = ca.case_labels[0]
        if not (isinstance(elem, Identifier) and elem.simple_name == "default"):
            p.append("case")
        self._print_container("", ca.padding.case_labels,
                              JContainer.Location.CASE_EXPRESSION, ",", "", p)
        self.visit_space(ca.padding.statements.before, Space.Location.CASE, p)
        self.visit_statements(ca.padding.statements.padding.elements,
                              JRightPadded.Location.CASE, p)
        if isinstance(ca.body, Statement):
            self.visit_right_padded(ca.padding.body,
                                    JRightPadded.Location.LANGUAGE_EXTENSION, p)
        else:
            self._print_right_padded(ca.padding.body,
                                     JRightPadded.Location.CASE_BODY, ";", p)
        self.after_syntax(ca, p)
        return ca

    def visit_catch(self, ca: Try.Catch, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(ca, Space.Location.CATCH_PREFIX, p)
        p.append("except")

        multi_variable = ca.parameter.tree
        self.before_syntax(multi_variable, Space.Location.VARIABLE_DECLARATIONS_PREFIX, p)
        self.visit(multi_variable.type_expression, p)

        for padded_variable in multi_variable.padding.variables:
            variable = padded_variable.element
            if variable.name.simple_name == "":
                continue
            self.visit_space(padded_variable.after, Space.Location.LANGUAGE_EXTENSION, p)
            self.before_syntax(variable, Space.Location.VARIABLE_PREFIX, p)
            p.append("as")
            self.visit(variable.name, p)
            self.after_syntax(variable, p)

        self.after_syntax(multi_variable, p)
        self.visit(ca.body, p)
        self.after_syntax(ca, p)
        return ca

    def visit_class_declaration(self, class_decl: ClassDeclaration, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(class_decl, Space.Location.CLASS_DECLARATION_PREFIX, p)
        self.visit_space(Space.EMPTY, Space.Location.ANNOTATIONS, p)
        self.visit(class_decl.leading_annotations, p)
        self.visit(class_decl.padding.kind.annotations, p)
        self.visit_space(class_decl.padding.kind.prefix,
                         Space.Location.CLASS_KIND, p)
        p.append("class")
        self.visit(class_decl.name, p)

        if class_decl.padding.implements is not None:
            omit_parens = class_decl.padding.implements.markers.find_first(
                OmitParentheses) is not None
            self._print_container("" if omit_parens else "(",
                                  class_decl.padding.implements,
                                  JContainer.Location.IMPLEMENTS, ",",
                                          "" if omit_parens else ")", p)

        self.visit(class_decl.body, p)
        self.after_syntax(class_decl, p)
        return class_decl

    def visit_control_parentheses(self, control_parens: ControlParentheses[J], p: PrintOutputCapture[P]) -> J:
        self.before_syntax(control_parens, Space.Location.CONTROL_PARENTHESES_PREFIX, p)
        self._print_right_padded(control_parens.padding.tree,
                                 JRightPadded.Location.PARENTHESES, "", p)
        self.after_syntax(control_parens, p)
        return control_parens

    def visit_else(self, else_: If.Else, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(else_, Space.Location.ELSE_PREFIX, p)
        parent = self.cursor.parent_tree_cursor().value
        if isinstance(parent, If) and isinstance(else_.body, If):
            p.append("el")
            self.visit(else_.body, p)
        elif isinstance(else_.body, Block):
            p.append("else")
            self.visit(else_.body, p)
        else:
            p.append("else")
            p.append(':')
            self.visit(else_.body, p)
        self.after_syntax(else_, p)
        return else_

    def visit_for_each_control(self, control: ForEachLoop.Control, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(control, Space.Location.FOR_EACH_CONTROL_PREFIX, p)
        self.visit_right_padded(control.padding.variable,
                                JRightPadded.Location.FOREACH_VARIABLE, p)
        p.append("in")
        self.visit_right_padded(control.padding.iterable,
                                JRightPadded.Location.FOREACH_ITERABLE, p)
        self.after_syntax(control, p)
        return control

    def visit_for_each_loop(self, for_each_loop: ForEachLoop, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(for_each_loop, Space.Location.FOR_EACH_LOOP_PREFIX, p)
        p.append("for")
        self.visit(for_each_loop.control, p)
        self.visit(for_each_loop.body, p)
        self.after_syntax(for_each_loop, p)
        return for_each_loop

    def visit_identifier(self, ident: Identifier, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(ident, Space.Location.IDENTIFIER_PREFIX, p)
        quoted = ident.markers.find_first(Quoted)
        style = {
            Quoted.Style.SINGLE: "'",
            Quoted.Style.DOUBLE: '"',
            Quoted.Style.TRIPLE_SINGLE: "'''",
            Quoted.Style.TRIPLE_DOUBLE: '"""',
        }

        if quoted is not None:
            p.append(style[quoted.style])
        p.append(ident.simple_name)
        if quoted is not None:
            p.append(style[quoted.style])
        self.after_syntax(ident, p)
        return ident

    def visit_if(self, iff: If, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(iff, Space.Location.IF_PREFIX, p)
        p.append("if")
        self.visit(iff.if_condition, p)

        then_part = iff.padding.then_part
        if not isinstance(then_part.element, Block):
            p.append(":")
        self._print_statement(then_part, JRightPadded.Location.IF_THEN, p)
        self.visit(iff.else_part, p)
        self.after_syntax(iff, p)
        return iff

    def visit_import(self, im: Import, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(im, Space.Location.IMPORT_PREFIX, p)
        if isinstance(im.qualid.target, Empty):
            self.visit(im.qualid.name, p)
        else:
            self.visit(im.qualid, p)
        self._print_left_padded("as", im.padding.alias,
                                JLeftPadded.Location.IMPORT_ALIAS_PREFIX, p)
        self.after_syntax(im, p)
        return im

    def visit_lambda(self, lambda_: Lambda, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(lambda_, Space.Location.LAMBDA_PREFIX, p)
        p.append("lambda")
        self.visit_space(lambda_.parameters.prefix,
                         Space.Location.LAMBDA_PARAMETERS_PREFIX, p)
        self.visit_markers(lambda_.parameters.markers, p)
        self._print_right_padded_list(lambda_.parameters.padding.parameters,
                                      JRightPadded.Location.LAMBDA_PARAM, ",", p)
        self.visit_space(lambda_.arrow, Space.Location.LAMBDA_ARROW_PREFIX, p)
        p.append(":")
        self.visit(lambda_.body, p)
        self.after_syntax(lambda_, p)
        return lambda_

    def visit_literal(self, literal: Literal, p: PrintOutputCapture[P]) -> J:
        if literal.value is None and literal.value_source is None:
            # currently, also `...` is mapped to a `None` value
            literal = literal.with_value_source("None")

        self.before_syntax(literal, Space.Location.LITERAL_PREFIX, p)
        unicode_escapes = literal.unicode_escapes
        if unicode_escapes is None:
            p.append(literal.value_source)
        elif literal.value_source is not None:
            surrogate_iter = iter(unicode_escapes)
            surrogate = next(surrogate_iter, None)
            i = 0
            if surrogate is not None and surrogate.value_source_index == 0:
                p.append("\\u").append(surrogate.code_point)
                surrogate = next(surrogate_iter, None)

            value_source_arr = list(literal.value_source)
            for c in value_source_arr:
                p.append(c)
                if surrogate is not None and surrogate.value_source_index == i + 1:
                    while surrogate is not None and surrogate.value_source_index == i + 1:
                        p.append("\\u").append(surrogate.code_point)
                        surrogate = next(surrogate_iter, None)
                    i += 1

        self.after_syntax(literal, p)
        return literal

    def visit_marker(self, marker: Marker, p: PrintOutputCapture[P]) -> Marker:
        return self.delegate.visit_marker(marker, p)

    def visit_method_declaration(self, method: MethodDeclaration, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(method, Space.Location.METHOD_DECLARATION_PREFIX, p)
        self.visit_space(Space.EMPTY, Space.Location.ANNOTATIONS, p)
        self.visit(method.leading_annotations, p)
        for m in method.modifiers:
            self.visit_modifier(m, p)

        # TODO: In java the method name is a J.Literal, which we can visit here its a string.
        # Maybe we won't need to visit the name at all.
        self.visit(method._name.identifier, p)
        self._print_container("(", method.padding.parameters,
                              JContainer.Location.METHOD_DECLARATION_PARAMETERS, ",", ")", p)
        self.visit(method.return_type_expression, p)
        self.visit(method.body, p)
        self.after_syntax(method, p)
        return method

    def visit_method_invocation(self, method: MethodInvocation, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(method, Space.Location.METHOD_INVOCATION_PREFIX, p)
        self._print_right_padded(method.padding.select,
                                 JRightPadded.Location.METHOD_SELECT,
                                         "" if method.name.simple_name == "" else ".", p)
        self._print_container("<", method.padding.type_parameters,
                              JContainer.Location.TYPE_PARAMETERS, ",", ">", p)
        self.visit(method.name, p)

        if method.markers.find_first(OmitParentheses) is not None:
            before = ""
            after = ""
        else:
            before = "("
            after = ")"

        self._print_container(before, method.padding.arguments,
                              JContainer.Location.METHOD_INVOCATION_ARGUMENTS, ",", after, p)
        self.after_syntax(method, p)
        return method

    def visit_modifier(self, mod: Modifier, p: PrintOutputCapture[P]) -> J:
        keyword_map = {
            Modifier.Type.Default: 'def',
            Modifier.Type.Async: 'async'
        }

        keyword = keyword_map.get(mod.type, None)
        if not keyword:
            raise ValueError(f"Unknown modifier: {mod.type}")

        if keyword:
            self.visit(mod.annotations, p)
            self.before_syntax(mod, Space.Location.MODIFIER_PREFIX, p)
            p.append(keyword)
            self.after_syntax(mod, p)
        return mod

    def visit_new_array(self, new_array: NewArray, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(new_array, Space.Location.NEW_ARRAY_PREFIX, p)
        self._print_container("[", new_array.padding.initializer,
                              JContainer.Location.NEW_ARRAY_INITIALIZER, ",", "]", p)
        self.after_syntax(new_array, p)
        return new_array

    def visit_parameterized_type(self, type_: ParameterizedType, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(type_, Space.Location.PARAMETERIZED_TYPE_PREFIX, p)
        self.visit(type_.clazz, p)
        self._print_container("[", type_.padding.type_parameters,
                              JContainer.Location.TYPE_PARAMETERS, ",", "]", p)
        self.after_syntax(type_, p)
        return type_

    def visit_switch(self, sw: Switch, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(sw, Space.Location.SWITCH_PREFIX, p)
        p.append("match")
        self.visit(sw.selector, p)
        self.visit(sw.cases, p)
        self.after_syntax(sw, p)
        return sw

    def visit_ternary(self, ternary: Ternary, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(ternary, Space.Location.TERNARY_PREFIX, p)
        self.visit(ternary.true_part, p)
        self.visit_space(ternary.padding.true_part.before,
                         Space.Location.TERNARY_TRUE, p)
        p.append("if")
        self.visit(ternary.condition, p)
        self._print_left_padded("else", ternary.padding.false_part,
                                JLeftPadded.Location.TERNARY_FALSE, p)
        self.after_syntax(ternary, p)
        return ternary

    def visit_throw(self, thrown: Throw, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(thrown, Space.Location.THROW_PREFIX, p)
        p.append("raise")
        self.visit(thrown.exception, p)
        self.after_syntax(thrown, p)
        return thrown

    def visit_try(self, tryable: Try, p: PrintOutputCapture[P]) -> J:
        is_with_statement = tryable.resources is not None and len(tryable.resources) > 0

        self.before_syntax(tryable, Space.Location.TRY_PREFIX, p)
        p.append("with") if is_with_statement else p.append("try")

        resources = tryable.padding.resources
        if is_with_statement and resources is not None:
            self.visit_space(resources.before, Space.Location.TRY_RESOURCES, p)
            omit_parentheses = resources.markers.find_first(OmitParentheses) is not None

            if not omit_parentheses:
                p.append("(")

            first = True
            for resource in resources.padding.elements:
                if not first:
                    p.append(",")
                else:
                    first = False

                self.visit_space(resource.element.prefix, Space.Location.TRY_RESOURCE, p)
                self.visit_markers(resource.element.markers, p)

                decl = resource.element.variable_declarations
                if isinstance(decl, Assignment):
                    assignment = decl
                    self.visit(assignment.assignment, p)
                    if not isinstance(assignment.variable, Empty):
                        self.visit_space(assignment.padding.assignment.before,
                                         Space.Location.LANGUAGE_EXTENSION, p)
                        p.append("as")
                        self.visit(assignment.variable, p)
                else:
                    self.visit(decl, p)

                self.visit_space(resource.after, Space.Location.TRY_RESOURCE_SUFFIX, p)
                self.visit_markers(resource.markers, p)

            self.visit_markers(resources.markers, p)
            if not omit_parentheses:
                p.append(")")

        try_body = tryable.body
        parent_cursor = self.cursor.parent_tree_cursor()
        parent_value = parent_cursor.value
        else_wrapper = parent_value if isinstance(parent_value, TrailingElseWrapper) else None

        self.visit(try_body, p)
        self.visit(tryable.catches, p)

        if else_wrapper is not None:
            self.visit_space(else_wrapper.padding.else_block.before,
                             Space.Location.ELSE_PREFIX, p)
            p.append("else")
            self.visit(else_wrapper.else_block, p)

        self._print_left_padded("finally", tryable.padding.finally_, JLeftPadded.Location.TRY_FINALLY, p)
        self.after_syntax(tryable, p)
        return tryable

    def visit_unary(self, unary: Unary, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(unary, Space.Location.UNARY_PREFIX, p)
        operator_map = {
            Unary.Type.Not: 'not',
            Unary.Type.Positive: '+',
            Unary.Type.Negative: '-',
            Unary.Type.Complement: '~'
        }
        op = operator_map.get(unary.operator, '')
        if not op:
            raise ValueError(f"Unknown unary operator: {unary.operator}")

        p.append(op)
        self.visit(unary.expression, p)
        self.after_syntax(unary, p)
        return unary

    def visit_variable(self, variable: VariableDeclarations.NamedVariable, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(variable, Space.Location.VARIABLE_PREFIX, p)
        vd = cast(VariableDeclarations, self.cursor.parent_tree_cursor().value)
        padding = cast(JRightPadded[VariableDeclarations.NamedVariable],
                       self.cursor.parent.value)  # pyright: ignore [reportOptionalMemberAccess]
        type_ = vd.type_expression

        if isinstance(type_, SpecialParameter):
            special = type_
            self.visit(special, p)
            type_ = special.type_hint

        if variable.name.simple_name == "":
            self.visit(variable.initializer, p)
        else:
            if vd.varargs is not None:
                self.visit_space(vd.varargs, Space.Location.VARARGS, p)
                p.append('*')
            if vd.markers.find_first(KeywordArguments) is not None:
                p.append("**")
            self.visit(variable.name, p)
            if type_ is not None:
                self.visit_space(padding.after,
                                 JRightPadded.Location.NAMED_VARIABLE.after_location, p)
                p.append(':')
                self.visit(type_, p)
            self._print_left_padded("=", variable.padding.initializer,
                                    JLeftPadded.Location.VARIABLE_INITIALIZER, p)
        self.after_syntax(variable, p)
        return variable

    def visit_variable_declarations(self, multi_variable: VariableDeclarations, p: PrintOutputCapture[P]) -> J:
        self.before_syntax(multi_variable, Space.Location.VARIABLE_DECLARATIONS_PREFIX, p)
        self.visit_space(Space.EMPTY, Space.Location.ANNOTATIONS, p)
        self.visit(multi_variable.leading_annotations, p)

        for m in multi_variable.modifiers:
            self.visit_modifier(m, p)

        if multi_variable.markers.find_first(KeywordOnlyArguments) is not None:
            p.append("*")

        nodes = multi_variable.padding.variables
        for i, node in enumerate(nodes):
            self.cursor = Cursor(self.cursor, node)
            self.visit(node.element, p)
            self.visit_markers(node.markers, p)
            if i < len(nodes) - 1:
                p.append(",")
            self.cursor = self.cursor.parent  # pyright: ignore [reportAttributeAccessIssue]

        self.after_syntax(multi_variable, p)
        return multi_variable
