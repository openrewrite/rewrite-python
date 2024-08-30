from typing import cast, TypeVar, Union

from rewrite import SourceFile, TreeVisitor
from .extensions import *
from .support_types import *
from .tree import *
from rewrite.java import JavaVisitor

# noinspection DuplicatedCode
class PythonVisitor(JavaVisitor[P]):
    def is_acceptable(self, source_file: SourceFile, p: P) -> bool:
        return isinstance(source_file, Py)

    def visit_python_binary(self, binary: Binary, p: P) -> J:
        binary = binary.with_prefix(self.visit_space(binary.prefix, PySpace.Location.BINARY_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(binary, p))
        if not isinstance(temp_expression, Binary):
            return temp_expression
        binary = cast(Binary, temp_expression)
        binary = binary.with_markers(self.visit_markers(binary.markers, p))
        binary = binary.with_left(self.visit_and_cast(binary.left, Expression, p))
        binary = binary.padding.with_operator(self.visit_left_padded(binary.padding.operator, PyLeftPadded.Location.BINARY_OPERATOR, p))
        binary = binary.with_negation(self.visit_space(binary.negation, PySpace.Location.BINARY_NEGATION, p))
        binary = binary.with_right(self.visit_and_cast(binary.right, Expression, p))
        return binary

    def visit_exception_type(self, exception_type: ExceptionType, p: P) -> J:
        exception_type = exception_type.with_prefix(self.visit_space(exception_type.prefix, PySpace.Location.EXCEPTION_TYPE_PREFIX, p))
        exception_type = exception_type.with_markers(self.visit_markers(exception_type.markers, p))
        exception_type = exception_type.with_expression(self.visit_and_cast(exception_type.expression, Expression, p))
        return exception_type

    def visit_type_hint(self, type_hint: TypeHint, p: P) -> J:
        type_hint = type_hint.with_prefix(self.visit_space(type_hint.prefix, PySpace.Location.TYPE_HINT_PREFIX, p))
        type_hint = type_hint.with_markers(self.visit_markers(type_hint.markers, p))
        type_hint = type_hint.with_type_tree(self.visit_and_cast(type_hint.type_tree, Expression, p))
        return type_hint

    def visit_compilation_unit(self, compilation_unit: CompilationUnit, p: P) -> J:
        compilation_unit = compilation_unit.with_prefix(self.visit_space(compilation_unit.prefix, Space.Location.COMPILATION_UNIT_PREFIX, p))
        compilation_unit = compilation_unit.with_markers(self.visit_markers(compilation_unit.markers, p))
        compilation_unit = compilation_unit.padding.with_imports([self.visit_right_padded(v, JRightPadded.Location.IMPORT, p) for v in compilation_unit.padding.imports])
        compilation_unit = compilation_unit.padding.with_statements([self.visit_right_padded(v, PyRightPadded.Location.COMPILATION_UNIT_STATEMENTS, p) for v in compilation_unit.padding.statements])
        compilation_unit = compilation_unit.with_eof(self.visit_space(compilation_unit.eof, Space.Location.COMPILATION_UNIT_EOF, p))
        return compilation_unit

    def visit_expression_statement(self, expression_statement: ExpressionStatement, p: P) -> J:
        expression_statement = expression_statement.with_expression(self.visit_and_cast(expression_statement.expression, Expression, p))
        return expression_statement

    def visit_statement_expression(self, statement_expression: StatementExpression, p: P) -> J:
        statement_expression = statement_expression.with_statement(self.visit_and_cast(statement_expression.statement, Statement, p))
        return statement_expression

    def visit_multi_import(self, multi_import: MultiImport, p: P) -> J:
        multi_import = multi_import.with_prefix(self.visit_space(multi_import.prefix, PySpace.Location.MULTI_IMPORT_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(multi_import, p))
        if not isinstance(temp_statement, MultiImport):
            return temp_statement
        multi_import = cast(MultiImport, temp_statement)
        multi_import = multi_import.with_markers(self.visit_markers(multi_import.markers, p))
        multi_import = multi_import.padding.with_from(self.visit_right_padded(multi_import.padding.from_, PyRightPadded.Location.MULTI_IMPORT_FROM, p))
        multi_import = multi_import.padding.with_names(self.visit_container(multi_import.padding.names, PyContainer.Location.MULTI_IMPORT_NAMES, p))
        return multi_import

    def visit_key_value(self, key_value: KeyValue, p: P) -> J:
        key_value = key_value.with_prefix(self.visit_space(key_value.prefix, PySpace.Location.KEY_VALUE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(key_value, p))
        if not isinstance(temp_expression, KeyValue):
            return temp_expression
        key_value = cast(KeyValue, temp_expression)
        key_value = key_value.with_markers(self.visit_markers(key_value.markers, p))
        key_value = key_value.padding.with_key(self.visit_right_padded(key_value.padding.key, PyRightPadded.Location.KEY_VALUE_KEY, p))
        key_value = key_value.with_value(self.visit_and_cast(key_value.value, Expression, p))
        return key_value

    def visit_dict_literal(self, dict_literal: DictLiteral, p: P) -> J:
        dict_literal = dict_literal.with_prefix(self.visit_space(dict_literal.prefix, PySpace.Location.DICT_LITERAL_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(dict_literal, p))
        if not isinstance(temp_expression, DictLiteral):
            return temp_expression
        dict_literal = cast(DictLiteral, temp_expression)
        dict_literal = dict_literal.with_markers(self.visit_markers(dict_literal.markers, p))
        dict_literal = dict_literal.padding.with_elements(self.visit_container(dict_literal.padding.elements, PyContainer.Location.DICT_LITERAL_ELEMENTS, p))
        return dict_literal

    def visit_collection_literal(self, collection_literal: CollectionLiteral, p: P) -> J:
        collection_literal = collection_literal.with_prefix(self.visit_space(collection_literal.prefix, PySpace.Location.COLLECTION_LITERAL_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(collection_literal, p))
        if not isinstance(temp_expression, CollectionLiteral):
            return temp_expression
        collection_literal = cast(CollectionLiteral, temp_expression)
        collection_literal = collection_literal.with_markers(self.visit_markers(collection_literal.markers, p))
        collection_literal = collection_literal.padding.with_elements(self.visit_container(collection_literal.padding.elements, PyContainer.Location.COLLECTION_LITERAL_ELEMENTS, p))
        return collection_literal

    def visit_formatted_string(self, formatted_string: FormattedString, p: P) -> J:
        formatted_string = formatted_string.with_prefix(self.visit_space(formatted_string.prefix, PySpace.Location.FORMATTED_STRING_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(formatted_string, p))
        if not isinstance(temp_expression, FormattedString):
            return temp_expression
        formatted_string = cast(FormattedString, temp_expression)
        formatted_string = formatted_string.with_markers(self.visit_markers(formatted_string.markers, p))
        formatted_string = formatted_string.with_parts([self.visit_and_cast(v, Expression, p) for v in formatted_string.parts])
        return formatted_string

    def visit_formatted_string_value(self, value: FormattedString.Value, p: P) -> J:
        value = value.with_prefix(self.visit_space(value.prefix, PySpace.Location.FORMATTED_STRING_VALUE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(value, p))
        if not isinstance(temp_expression, FormattedString.Value):
            return temp_expression
        value = cast(FormattedString.Value, temp_expression)
        value = value.with_markers(self.visit_markers(value.markers, p))
        value = value.padding.with_expression(self.visit_right_padded(value.padding.expression, PyRightPadded.Location.FORMATTED_STRING_VALUE_EXPRESSION, p))
        value = value.padding.with_debug(self.visit_right_padded(value.padding.debug, PyRightPadded.Location.FORMATTED_STRING_VALUE_DEBUG, p))
        value = value.with_format(self.visit_and_cast(value.format, Expression, p))
        return value

    def visit_pass(self, pass_: Pass, p: P) -> J:
        pass_ = pass_.with_prefix(self.visit_space(pass_.prefix, PySpace.Location.PASS_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(pass_, p))
        if not isinstance(temp_statement, Pass):
            return temp_statement
        pass_ = cast(Pass, temp_statement)
        pass_ = pass_.with_markers(self.visit_markers(pass_.markers, p))
        return pass_

    def visit_trailing_else_wrapper(self, trailing_else_wrapper: TrailingElseWrapper, p: P) -> J:
        trailing_else_wrapper = trailing_else_wrapper.with_prefix(self.visit_space(trailing_else_wrapper.prefix, PySpace.Location.TRAILING_ELSE_WRAPPER_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(trailing_else_wrapper, p))
        if not isinstance(temp_statement, TrailingElseWrapper):
            return temp_statement
        trailing_else_wrapper = cast(TrailingElseWrapper, temp_statement)
        trailing_else_wrapper = trailing_else_wrapper.with_markers(self.visit_markers(trailing_else_wrapper.markers, p))
        trailing_else_wrapper = trailing_else_wrapper.with_statement(self.visit_and_cast(trailing_else_wrapper.statement, Statement, p))
        trailing_else_wrapper = trailing_else_wrapper.padding.with_else_block(self.visit_left_padded(trailing_else_wrapper.padding.else_block, PyLeftPadded.Location.TRAILING_ELSE_WRAPPER_ELSE_BLOCK, p))
        return trailing_else_wrapper

    def visit_comprehension_expression(self, comprehension_expression: ComprehensionExpression, p: P) -> J:
        comprehension_expression = comprehension_expression.with_prefix(self.visit_space(comprehension_expression.prefix, PySpace.Location.COMPREHENSION_EXPRESSION_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(comprehension_expression, p))
        if not isinstance(temp_expression, ComprehensionExpression):
            return temp_expression
        comprehension_expression = cast(ComprehensionExpression, temp_expression)
        comprehension_expression = comprehension_expression.with_markers(self.visit_markers(comprehension_expression.markers, p))
        comprehension_expression = comprehension_expression.with_result(self.visit_and_cast(comprehension_expression.result, Expression, p))
        comprehension_expression = comprehension_expression.with_clauses([self.visit_and_cast(v, ComprehensionExpression.Clause, p) for v in comprehension_expression.clauses])
        comprehension_expression = comprehension_expression.with_suffix(self.visit_space(comprehension_expression.suffix, PySpace.Location.COMPREHENSION_EXPRESSION_SUFFIX, p))
        return comprehension_expression

    def visit_comprehension_condition(self, condition: ComprehensionExpression.Condition, p: P) -> J:
        condition = condition.with_prefix(self.visit_space(condition.prefix, PySpace.Location.COMPREHENSION_EXPRESSION_CONDITION_PREFIX, p))
        condition = condition.with_markers(self.visit_markers(condition.markers, p))
        condition = condition.with_expression(self.visit_and_cast(condition.expression, Expression, p))
        return condition

    def visit_comprehension_clause(self, clause: ComprehensionExpression.Clause, p: P) -> J:
        clause = clause.with_prefix(self.visit_space(clause.prefix, PySpace.Location.COMPREHENSION_EXPRESSION_CLAUSE_PREFIX, p))
        clause = clause.with_markers(self.visit_markers(clause.markers, p))
        clause = clause.with_iterator_variable(self.visit_and_cast(clause.iterator_variable, Expression, p))
        clause = clause.padding.with_iterated_list(self.visit_left_padded(clause.padding.iterated_list, PyLeftPadded.Location.COMPREHENSION_EXPRESSION_CLAUSE_ITERATED_LIST, p))
        clause = clause.with_conditions([self.visit_and_cast(v, ComprehensionExpression.Condition, p) for v in clause.conditions])
        return clause

    def visit_await(self, await_: Await, p: P) -> J:
        await_ = await_.with_prefix(self.visit_space(await_.prefix, PySpace.Location.AWAIT_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(await_, p))
        if not isinstance(temp_expression, Await):
            return temp_expression
        await_ = cast(Await, temp_expression)
        await_ = await_.with_markers(self.visit_markers(await_.markers, p))
        await_ = await_.with_expression(self.visit_and_cast(await_.expression, Expression, p))
        return await_

    def visit_yield_from(self, yield_from: YieldFrom, p: P) -> J:
        yield_from = yield_from.with_prefix(self.visit_space(yield_from.prefix, PySpace.Location.YIELD_FROM_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(yield_from, p))
        if not isinstance(temp_expression, YieldFrom):
            return temp_expression
        yield_from = cast(YieldFrom, temp_expression)
        yield_from = yield_from.with_markers(self.visit_markers(yield_from.markers, p))
        yield_from = yield_from.with_expression(self.visit_and_cast(yield_from.expression, Expression, p))
        return yield_from

    def visit_variable_scope(self, variable_scope: VariableScope, p: P) -> J:
        variable_scope = variable_scope.with_prefix(self.visit_space(variable_scope.prefix, PySpace.Location.VARIABLE_SCOPE_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(variable_scope, p))
        if not isinstance(temp_statement, VariableScope):
            return temp_statement
        variable_scope = cast(VariableScope, temp_statement)
        variable_scope = variable_scope.with_markers(self.visit_markers(variable_scope.markers, p))
        variable_scope = variable_scope.padding.with_names([self.visit_right_padded(v, PyRightPadded.Location.VARIABLE_SCOPE_NAMES, p) for v in variable_scope.padding.names])
        return variable_scope

    def visit_del(self, del_: Del, p: P) -> J:
        del_ = del_.with_prefix(self.visit_space(del_.prefix, PySpace.Location.DEL_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(del_, p))
        if not isinstance(temp_statement, Del):
            return temp_statement
        del_ = cast(Del, temp_statement)
        del_ = del_.with_markers(self.visit_markers(del_.markers, p))
        del_ = del_.padding.with_targets([self.visit_right_padded(v, PyRightPadded.Location.DEL_TARGETS, p) for v in del_.padding.targets])
        return del_

    def visit_special_parameter(self, special_parameter: SpecialParameter, p: P) -> J:
        special_parameter = special_parameter.with_prefix(self.visit_space(special_parameter.prefix, PySpace.Location.SPECIAL_PARAMETER_PREFIX, p))
        special_parameter = special_parameter.with_markers(self.visit_markers(special_parameter.markers, p))
        special_parameter = special_parameter.with_type_hint(self.visit_and_cast(special_parameter.type_hint, TypeHint, p))
        return special_parameter

    def visit_star(self, star: Star, p: P) -> J:
        star = star.with_prefix(self.visit_space(star.prefix, PySpace.Location.STAR_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(star, p))
        if not isinstance(temp_expression, Star):
            return temp_expression
        star = cast(Star, temp_expression)
        star = star.with_markers(self.visit_markers(star.markers, p))
        star = star.with_expression(self.visit_and_cast(star.expression, Expression, p))
        return star

    def visit_named_argument(self, named_argument: NamedArgument, p: P) -> J:
        named_argument = named_argument.with_prefix(self.visit_space(named_argument.prefix, PySpace.Location.NAMED_ARGUMENT_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(named_argument, p))
        if not isinstance(temp_expression, NamedArgument):
            return temp_expression
        named_argument = cast(NamedArgument, temp_expression)
        named_argument = named_argument.with_markers(self.visit_markers(named_argument.markers, p))
        named_argument = named_argument.with_name(self.visit_and_cast(named_argument.name, Identifier, p))
        named_argument = named_argument.padding.with_value(self.visit_left_padded(named_argument.padding.value, PyLeftPadded.Location.NAMED_ARGUMENT_VALUE, p))
        return named_argument

    def visit_type_hinted_expression(self, type_hinted_expression: TypeHintedExpression, p: P) -> J:
        type_hinted_expression = type_hinted_expression.with_prefix(self.visit_space(type_hinted_expression.prefix, PySpace.Location.TYPE_HINTED_EXPRESSION_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(type_hinted_expression, p))
        if not isinstance(temp_expression, TypeHintedExpression):
            return temp_expression
        type_hinted_expression = cast(TypeHintedExpression, temp_expression)
        type_hinted_expression = type_hinted_expression.with_markers(self.visit_markers(type_hinted_expression.markers, p))
        type_hinted_expression = type_hinted_expression.with_type_hint(self.visit_and_cast(type_hinted_expression.type_hint, TypeHint, p))
        type_hinted_expression = type_hinted_expression.with_expression(self.visit_and_cast(type_hinted_expression.expression, Expression, p))
        return type_hinted_expression

    def visit_error_from(self, error_from: ErrorFrom, p: P) -> J:
        error_from = error_from.with_prefix(self.visit_space(error_from.prefix, PySpace.Location.ERROR_FROM_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(error_from, p))
        if not isinstance(temp_expression, ErrorFrom):
            return temp_expression
        error_from = cast(ErrorFrom, temp_expression)
        error_from = error_from.with_markers(self.visit_markers(error_from.markers, p))
        error_from = error_from.with_error(self.visit_and_cast(error_from.error, Expression, p))
        error_from = error_from.padding.with_from(self.visit_left_padded(error_from.padding.from_, PyLeftPadded.Location.ERROR_FROM_FROM, p))
        return error_from

    def visit_match_case(self, match_case: MatchCase, p: P) -> J:
        match_case = match_case.with_prefix(self.visit_space(match_case.prefix, PySpace.Location.MATCH_CASE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(match_case, p))
        if not isinstance(temp_expression, MatchCase):
            return temp_expression
        match_case = cast(MatchCase, temp_expression)
        match_case = match_case.with_markers(self.visit_markers(match_case.markers, p))
        match_case = match_case.with_pattern(self.visit_and_cast(match_case.pattern, MatchCase.Pattern, p))
        match_case = match_case.padding.with_guard(self.visit_left_padded(match_case.padding.guard, PyLeftPadded.Location.MATCH_CASE_GUARD, p))
        return match_case

    def visit_match_case_pattern(self, pattern: MatchCase.Pattern, p: P) -> J:
        pattern = pattern.with_prefix(self.visit_space(pattern.prefix, PySpace.Location.MATCH_CASE_PATTERN_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(pattern, p))
        if not isinstance(temp_expression, MatchCase.Pattern):
            return temp_expression
        pattern = cast(MatchCase.Pattern, temp_expression)
        pattern = pattern.with_markers(self.visit_markers(pattern.markers, p))
        pattern = pattern.padding.with_children(self.visit_container(pattern.padding.children, PyContainer.Location.MATCH_CASE_PATTERN_CHILDREN, p))
        return pattern

    def visit_slice(self, slice: Slice, p: P) -> J:
        slice = slice.with_prefix(self.visit_space(slice.prefix, PySpace.Location.SLICE_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(slice, p))
        if not isinstance(temp_expression, Slice):
            return temp_expression
        slice = cast(Slice, temp_expression)
        slice = slice.with_markers(self.visit_markers(slice.markers, p))
        slice = slice.padding.with_start(self.visit_right_padded(slice.padding.start, PyRightPadded.Location.SLICE_START, p))
        slice = slice.padding.with_stop(self.visit_right_padded(slice.padding.stop, PyRightPadded.Location.SLICE_STOP, p))
        slice = slice.padding.with_step(self.visit_right_padded(slice.padding.step, PyRightPadded.Location.SLICE_STEP, p))
        return slice

    def visit_container(self, container: Optional[JContainer[J2]], loc: Union[PyContainer.Location, JContainer.Location], p: P) -> JContainer[J2]:
        if isinstance(loc, JContainer.Location):
            return super().visit_container(container, loc, p)
        return extensions.visit_container(self, container, loc, p)

    def visit_right_padded(self, right: Optional[JRightPadded[T]], loc: Union[PyRightPadded.Location, JRightPadded.Location], p: P) -> Optional[JRightPadded[T]]:
        if isinstance(loc, JRightPadded.Location):
            return super().visit_right_padded(right, loc, p)
        return extensions.visit_right_padded(self, right, loc, p)

    def visit_left_padded(self, left: Optional[JLeftPadded[T]], loc: PyLeftPadded.Location, p: P) -> Optional[JLeftPadded[T]]:
        if isinstance(loc, JLeftPadded.Location):
            return super().visit_left_padded(left, loc, p)
        return extensions.visit_left_padded(self, left, loc, p)

    def visit_space(self, space: Optional[Space], loc: Optional[Union[PySpace.Location, Space.Location]], p: P) -> Space:
        if isinstance(loc, Space.Location) or loc is None:
            return super().visit_space(space, loc, p)
        return extensions.visit_space(self, space, loc, p)
