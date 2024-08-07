from typing import cast, TypeVar, Union

from rewrite import TreeVisitor
from .tree import *
from rewrite.java.visitor import JavaVisitor

P = TypeVar('P')

# noinspection DuplicatedCode
class PythonVisitor(JavaVisitor[P]):
    def is_acceptable(self, source_file: SourceFile, p: P) -> bool:
        return isinstance(source_file, Py)

    def visit_exception_type(self, exception_type: ExceptionType, p: P) -> J:
        exception_type = exception_type.with_prefix(self.visit_space(exception_type.prefix, PySpace.Location.EXCEPTION_TYPE_PREFIX, p))
        exception_type = exception_type.with_markers(self.visit_markers(exception_type.markers, p))
        exception_type = exception_type.with_expression(self.visit_and_cast(exception_type.expression, Expression, p))
        return exception_type

    def visit_type_hint(self, type_hint: TypeHint, p: P) -> J:
        type_hint = type_hint.with_prefix(self.visit_space(type_hint.prefix, PySpace.Location.TYPE_HINT_PREFIX, p))
        type_hint = type_hint.with_markers(self.visit_markers(type_hint.markers, p))
        type_hint = type_hint.with_expression(self.visit_and_cast(type_hint.expression, Expression, p))
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

    def visit_pass_statement(self, pass_statement: PassStatement, p: P) -> J:
        pass_statement = pass_statement.with_prefix(self.visit_space(pass_statement.prefix, PySpace.Location.PASS_STATEMENT_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(pass_statement, p))
        if not isinstance(temp_statement, PassStatement):
            return temp_statement
        pass_statement = cast(PassStatement, temp_statement)
        pass_statement = pass_statement.with_markers(self.visit_markers(pass_statement.markers, p))
        return pass_statement

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

    def visit_comprehension_expression_condition(self, condition: ComprehensionExpression.Condition, p: P) -> J:
        condition = condition.with_prefix(self.visit_space(condition.prefix, PySpace.Location.COMPREHENSION_EXPRESSION_CONDITION_PREFIX, p))
        condition = condition.with_markers(self.visit_markers(condition.markers, p))
        condition = condition.with_expression(self.visit_and_cast(condition.expression, Expression, p))
        return condition

    def visit_comprehension_expression_clause(self, clause: ComprehensionExpression.Clause, p: P) -> J:
        clause = clause.with_prefix(self.visit_space(clause.prefix, PySpace.Location.COMPREHENSION_EXPRESSION_CLAUSE_PREFIX, p))
        clause = clause.with_markers(self.visit_markers(clause.markers, p))
        clause = clause.with_iterator_variable(self.visit_and_cast(clause.iterator_variable, Expression, p))
        clause = clause.padding.with_iterated_list(self.visit_left_padded(clause.padding.iterated_list, PyLeftPadded.Location.COMPREHENSION_EXPRESSION_CLAUSE_ITERATED_LIST, p))
        clause = clause.with_conditions([self.visit_and_cast(v, ComprehensionExpression.Condition, p) for v in clause.conditions])
        return clause

    def visit_await_expression(self, await_expression: AwaitExpression, p: P) -> J:
        await_expression = await_expression.with_prefix(self.visit_space(await_expression.prefix, PySpace.Location.AWAIT_EXPRESSION_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(await_expression, p))
        if not isinstance(temp_expression, AwaitExpression):
            return temp_expression
        await_expression = cast(AwaitExpression, temp_expression)
        await_expression = await_expression.with_markers(self.visit_markers(await_expression.markers, p))
        await_expression = await_expression.with_expression(self.visit_and_cast(await_expression.expression, Expression, p))
        return await_expression

    def visit_yield_expression(self, yield_expression: YieldExpression, p: P) -> J:
        yield_expression = yield_expression.with_prefix(self.visit_space(yield_expression.prefix, PySpace.Location.YIELD_EXPRESSION_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(yield_expression, p))
        if not isinstance(temp_expression, YieldExpression):
            return temp_expression
        yield_expression = cast(YieldExpression, temp_expression)
        yield_expression = yield_expression.with_markers(self.visit_markers(yield_expression.markers, p))
        yield_expression = yield_expression.padding.with_from(self.visit_left_padded(yield_expression.padding.from_, PyLeftPadded.Location.YIELD_EXPRESSION_FROM, p))
        yield_expression = yield_expression.padding.with_expressions([self.visit_right_padded(v, PyRightPadded.Location.YIELD_EXPRESSION_EXPRESSIONS, p) for v in yield_expression.padding.expressions])
        return yield_expression

    def visit_variable_scope_statement(self, variable_scope_statement: VariableScopeStatement, p: P) -> J:
        variable_scope_statement = variable_scope_statement.with_prefix(self.visit_space(variable_scope_statement.prefix, PySpace.Location.VARIABLE_SCOPE_STATEMENT_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(variable_scope_statement, p))
        if not isinstance(temp_statement, VariableScopeStatement):
            return temp_statement
        variable_scope_statement = cast(VariableScopeStatement, temp_statement)
        variable_scope_statement = variable_scope_statement.with_markers(self.visit_markers(variable_scope_statement.markers, p))
        variable_scope_statement = variable_scope_statement.padding.with_names([self.visit_right_padded(v, PyRightPadded.Location.VARIABLE_SCOPE_STATEMENT_NAMES, p) for v in variable_scope_statement.padding.names])
        return variable_scope_statement

    def visit_assert_statement(self, assert_statement: AssertStatement, p: P) -> J:
        assert_statement = assert_statement.with_prefix(self.visit_space(assert_statement.prefix, PySpace.Location.ASSERT_STATEMENT_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(assert_statement, p))
        if not isinstance(temp_statement, AssertStatement):
            return temp_statement
        assert_statement = cast(AssertStatement, temp_statement)
        assert_statement = assert_statement.with_markers(self.visit_markers(assert_statement.markers, p))
        assert_statement = assert_statement.padding.with_expressions([self.visit_right_padded(v, PyRightPadded.Location.ASSERT_STATEMENT_EXPRESSIONS, p) for v in assert_statement.padding.expressions])
        return assert_statement

    def visit_del_statement(self, del_statement: DelStatement, p: P) -> J:
        del_statement = del_statement.with_prefix(self.visit_space(del_statement.prefix, PySpace.Location.DEL_STATEMENT_PREFIX, p))
        temp_statement = cast(Statement, self.visit_statement(del_statement, p))
        if not isinstance(temp_statement, DelStatement):
            return temp_statement
        del_statement = cast(DelStatement, temp_statement)
        del_statement = del_statement.with_markers(self.visit_markers(del_statement.markers, p))
        del_statement = del_statement.padding.with_targets([self.visit_right_padded(v, PyRightPadded.Location.DEL_STATEMENT_TARGETS, p) for v in del_statement.padding.targets])
        return del_statement

    def visit_special_parameter(self, special_parameter: SpecialParameter, p: P) -> J:
        special_parameter = special_parameter.with_prefix(self.visit_space(special_parameter.prefix, PySpace.Location.SPECIAL_PARAMETER_PREFIX, p))
        special_parameter = special_parameter.with_markers(self.visit_markers(special_parameter.markers, p))
        special_parameter = special_parameter.with_type_hint(self.visit_and_cast(special_parameter.type_hint, TypeHint, p))
        return special_parameter

    def visit_special_argument(self, special_argument: SpecialArgument, p: P) -> J:
        special_argument = special_argument.with_prefix(self.visit_space(special_argument.prefix, PySpace.Location.SPECIAL_ARGUMENT_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(special_argument, p))
        if not isinstance(temp_expression, SpecialArgument):
            return temp_expression
        special_argument = cast(SpecialArgument, temp_expression)
        special_argument = special_argument.with_markers(self.visit_markers(special_argument.markers, p))
        special_argument = special_argument.with_expression(self.visit_and_cast(special_argument.expression, Expression, p))
        return special_argument

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

    def visit_error_from_expression(self, error_from_expression: ErrorFromExpression, p: P) -> J:
        error_from_expression = error_from_expression.with_prefix(self.visit_space(error_from_expression.prefix, PySpace.Location.ERROR_FROM_EXPRESSION_PREFIX, p))
        temp_expression = cast(Expression, self.visit_expression(error_from_expression, p))
        if not isinstance(temp_expression, ErrorFromExpression):
            return temp_expression
        error_from_expression = cast(ErrorFromExpression, temp_expression)
        error_from_expression = error_from_expression.with_markers(self.visit_markers(error_from_expression.markers, p))
        error_from_expression = error_from_expression.with_error(self.visit_and_cast(error_from_expression.error, Expression, p))
        error_from_expression = error_from_expression.padding.with_from(self.visit_left_padded(error_from_expression.padding.from_, PyLeftPadded.Location.ERROR_FROM_EXPRESSION_FROM, p))
        return error_from_expression

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
