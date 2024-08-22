import ast
from io import BytesIO
from pathlib import Path
from tokenize import tokenize
from typing import Optional, TypeVar, cast, Callable, List, Tuple, Dict, Type, Union

from rewrite import random_id, Markers
from rewrite.java import Space, JRightPadded, JContainer, JLeftPadded, JavaType, TextComment, J, Statement, \
    Semicolon, TrailingComma
from rewrite.java import tree as j
from . import tree as py

J2 = TypeVar('J2', bound=J)


class ParserVisitor(ast.NodeVisitor):
    _source: str
    _cursor: int = 0
    _parentheses_stack: List[Tuple[Callable[[J, Space], j.Parentheses], Tuple[int, int]]] = []

    def __init__(self, source: str):
        super().__init__()
        self._source = source

    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_arguments(self, node) -> JContainer[j.VariableDeclarations]:
        first_with_default = len(node.args) - len(node.defaults)
        prefix = self.__source_before('(')
        args = JContainer(prefix, [self.__pad_right(
            self.map_arg(a, node.defaults[i - len(node.defaults)] if i >= first_with_default else None),
            self.__source_before(',')) for i, a in enumerate(node.args)], Markers.EMPTY)
        self.__skip(')')
        return args

    def map_arg(self, node, default=None):
        prefix = self.__source_before(node.arg)
        name = j.Identifier(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            [],
            node.arg,
            self.__map_type(node),
            None
        )
        var = self.__pad_right(j.VariableDeclarations.NamedVariable(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            name,
            [],
            self.__pad_left(self.__source_before('='), self.__convert(default)) if default else None,
            self.__map_type(node)
        ), self.__source_before(':') if node.annotation else Space.EMPTY)

        type_expression = self.__convert(node.annotation) if node.annotation else None

        return j.VariableDeclarations(
            random_id(),
            prefix,
            Markers.EMPTY,
            [],
            [],
            type_expression,
            None,
            [],
            [var],
        )

    def visit_Assert(self, node):
        return j.Assert(
            random_id(),
            self.__source_before('assert'),
            Markers.EMPTY,
            self.__convert(node.test),
            self.__pad_left(self.__source_before(','), self.__convert(node.msg)) if node.msg else None,
        )

    def visit_Assign(self, node):
        if (len(node.targets) == 1):
            return j.Assignment(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                self.__convert(node.targets[0]),
                self.__pad_left(self.__source_before('='), self.__convert(node.value)),
                self.__map_type(node.value)
            )
        else:
            # FIXME implement me
            raise NotImplementedError("Multiple assignments are not yet supported")

    def visit_AugAssign(self, node):
        return j.AssignmentOperation(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            self.__convert(node.target),
            self._map_assignment_operator(node.op),
            self.__convert(node.value),
            self.__map_type(node)
        )

    def visit_Await(self, node):
        return py.AwaitExpression(
            random_id(),
            self.__source_before('await'),
            Markers.EMPTY,
            self.__convert(node.value),
            self.__map_type(node)
        )

    def visit_BinOp(self, node):
        return j.Binary(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            self.__convert(node.left),
            self._map_binary_operator(node.op),
            self.__convert(node.right),
            self.__map_type(node)
        )

    def visit_BoolOp(self, node):
        binaries = []
        prefix = self.__whitespace()
        left = self.__convert(node.values[0])
        for right_expr in node.values[1:]:
            left = j.Binary(
                random_id(),
                prefix,
                Markers.EMPTY,
                left,
                self._map_binary_operator(node.op),
                self.__convert(right_expr),
                self.__map_type(node)
            )
            binaries.append(left)
            prefix = Space.EMPTY

        return binaries[-1]

    def visit_Call(self, node):
        prefix = self.__whitespace()
        if isinstance(node.func, ast.Name):
            name = cast(j.Identifier, self.__convert(node.func))
            parens_prefix = self.__source_before('(')
            args = JContainer(parens_prefix,
                              [self.__pad_right(self.__convert(a), self.__source_before(',')) for a in node.args],
                              Markers.EMPTY)
            self.__skip(')')

            return j.MethodInvocation(
                random_id(),
                prefix,
                Markers.EMPTY,
                None,  # TODO
                None,
                name,
                args,  # TODO
                self.__map_type(node)
            )
        elif isinstance(node.func, ast.Attribute):
            select = self.__pad_right(self.__convert(node.func.value), self.__source_before('.'))
            name = j.Identifier(
                random_id(),
                self.__source_before(node.func.attr),
                Markers.EMPTY,
                [],
                node.func.attr,
                self.__map_type(node.func.value),
                None
            )
            parens_prefix = self.__source_before('(')
            args = JContainer(parens_prefix,
                              [self.__pad_right(self.__convert(a), self.__source_before(',')) for a in
                               node.args] if node.args else [
                                  self.__pad_right(j.Empty(random_id(), self.__whitespace(), Markers.EMPTY),
                                                   Space.EMPTY)],
                              Markers.EMPTY)

            self.__skip(')')

            return j.MethodInvocation(
                random_id(),
                prefix,
                Markers.EMPTY,
                select,
                None,
                name,
                args,  # TODO
                self.__map_type(node)
            )
        else:
            raise NotImplementedError("Calls to functions other than methods are not yet supported")

    def visit_Compare(self, node):
        if len(node.ops) != 1:
            raise NotImplementedError("Multiple comparisons are not yet supported")

        return j.Binary(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            self.__convert(node.left),
            self._map_binary_operator(node.ops[0]),
            self.__convert(node.comparators[0]),
            self.__map_type(node)
        )

    def _map_binary_operator(self, op) -> JLeftPadded[j.Binary.Type]:
        operation_map: Dict[Type[ast], Tuple[j.Binary.Type, str]] = {
            ast.Add: (j.Binary.Type.Addition, '+'),
            ast.And: (j.Binary.Type.And, 'and'),
            ast.BitAnd: (j.Binary.Type.BitAnd, '&'),
            ast.BitOr: (j.Binary.Type.BitOr, '|'),
            ast.BitXor: (j.Binary.Type.BitXor, '^'),
            ast.Div: (j.Binary.Type.Division, '/'),
            ast.Eq: (j.Binary.Type.Equal, '=='),
            ast.Gt: (j.Binary.Type.GreaterThan, '>'),
            ast.GtE: (j.Binary.Type.GreaterThanOrEqual, '>='),
            ast.LShift: (j.Binary.Type.LeftShift, '<<'),
            ast.Lt: (j.Binary.Type.LessThan, '<'),
            ast.LtE: (j.Binary.Type.LessThanOrEqual, '<='),
            ast.Mod: (j.Binary.Type.Modulo, '%'),
            ast.Mult: (j.Binary.Type.Multiplication, '*'),
            ast.NotEq: (j.Binary.Type.NotEqual, '!='),
            ast.Or: (j.Binary.Type.Or, 'or'),
            ast.RShift: (j.Binary.Type.RightShift, '>>'),
            ast.Sub: (j.Binary.Type.Subtraction, '-'),
        }
        try:
            op, op_str = operation_map[type(op)]
        except KeyError:
            raise ValueError(f"Unsupported operator: {op}")
        return self.__pad_left(self.__source_before(op_str), op)

    def visit_Constant(self, node):
        # noinspection PyTypeChecker
        type_: JavaType.Primitive = self.__map_type(node)
        prefix = self.__whitespace()

        # TODO temporary solution
        tokens = tokenize(BytesIO(self._source[self._cursor:].encode('utf-8')).readline)
        next(tokens)  # skip ENCODING token
        value_source = next(tokens).string
        self._cursor += len(value_source)

        return j.Literal(
            random_id(),
            prefix,
            Markers.EMPTY,
            node.value,
            value_source,
            None,
            type_,
        )

    def visit_Dict(self, node):
        dict = py.DictLiteral(
            random_id(),
            self.__source_before('{'),
            Markers.EMPTY,
            JContainer(
                Space.EMPTY,
                [self.__pad_right(j.Empty(random_id(), self.__whitespace(), Markers.EMPTY),
                                  Space.EMPTY)] if not node.keys else
                [self._map_dict_entry(k, v, i == len(node.keys) - 1) for i, (k, v) in enumerate(zip(node.keys, node.values))],
                Markers.EMPTY
            ),
            self.__map_type(node)
        )
        self.__skip('}')
        return dict

    def visit_DictComp(self, node):
        self.__skip('for')
        return py.ComprehensionExpression(
            random_id(),
            self.__source_before('{'),
            Markers.EMPTY,
            py.ComprehensionExpression.Kind.DICT,
            py.KeyValue(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                self.__pad_right(self.__convert(node.key), self.__source_before(':')),
                self.__convert(node.value),
                self.__map_type(node.value)
            ),
            cast(List[py.ComprehensionExpression.Clause], [self.__convert(g) for g in node.generators]),
            self.__source_before('}'),
            self.__map_type(node)
        )

    def _map_dict_entry(self, key: Optional[ast.expr], value: ast.expr, last: bool) -> JRightPadded[J]:
        if key is None:
            element = py.StarExpression(
                random_id(),
                self.__source_before('**'),
                Markers.EMPTY,
                py.StarExpression.Kind.DICT,
                self.__convert(value),
                self.__map_type(value),
            )
        else:
            element = py.KeyValue(random_id(), self.__whitespace(), Markers.EMPTY,
                                  self.__pad_right(self.__convert(key), self.__source_before(':')), self.__convert(value),
                                  self.__map_type(value))
        return self.__pad_list_element(element, last)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> j.MethodDeclaration:
        save_cursor = self._cursor
        async_prefix = self.__source_before('async')
        modifiers = []
        if save_cursor != self._cursor:
            modifiers.append(j.Modifier(
                random_id(),
                async_prefix,
                Markers.EMPTY,
                'async',
                j.Modifier.Type.Async,
                []
            ))
        save_cursor = self._cursor
        def_prefix = self.__source_before('def')
        if save_cursor != self._cursor:
            modifiers.append(j.Modifier(
                random_id(),
                def_prefix,
                Markers.EMPTY,
                'def',
                j.Modifier.Type.Default,
                []
            ))
        name = j.MethodDeclaration.IdentifierWithAnnotations(j.Identifier(
            random_id(),
            self.__source_before(node.name),
            Markers.EMPTY,
            [],
            node.name,
            None,
            None
        ), [])

        params = self.visit_arguments(node.args)
        return_type = self.__convert(node.returns) if node.returns else None
        body = j.Block(
            random_id(),
            self.__source_before(':'),
            Markers.EMPTY,
            self.__pad_right(False, Space.EMPTY),
            [self.__pad_statement(stmt) for stmt in node.body] if node.body else [
                self.__pad_right(j.Empty(random_id(), Space.EMPTY, Markers.EMPTY), Space.EMPTY)],
            Space.EMPTY
        )

        return j.MethodDeclaration(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            [],
            modifiers,
            None,
            return_type,
            name,
            params,
            None,
            body,
            None,
            self.__map_type(node),
        )

    def visit_IfExp(self, node):
        # TODO check if we actually want to use `J.Ternary` as it requires "reversing" some of the padding
        prefix = self.__whitespace()
        true_expr = self.__convert(node.body)
        true_part = self.__pad_left(self.__source_before('if'), true_expr)
        condition = self.__convert(node.test)
        false_part = self.__pad_left(self.__source_before('else'), self.__convert(node.orelse))
        return j.Ternary(
            random_id(),
            prefix,
            Markers.EMPTY,
            condition,
            true_part,
            false_part,
            self.__map_type(node)
        )

    def visit_JoinedStr(self, node):
        prefix = self.__whitespace()
        tokens = tokenize(BytesIO(self._source[self._cursor:].encode('utf-8')).readline)
        next(tokens)  # skip ENCODING token
        value_source = next(tokens).string
        delimiter = value_source[0:2]
        return py.FormattedString(
            random_id(),
            prefix,
            Markers.EMPTY,
            delimiter,
            JContainer(Space.EMPTY, [self.__pad_right(self.__convert(p), Space.EMPTY) for p in node.values], Markers.EMPTY)
        )

    def visit_FormattedValue(self, node):
        return py.FormattedValue(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            self.__convert(node.value),
        )

    def visit_Lambda(self, node):
        first_with_default = len(node.args.args) - len(node.args.defaults)
        return j.Lambda(
            random_id(),
            self.__source_before('lambda'),
            Markers.EMPTY,
            j.Lambda.Parameters(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                False,
                [self.__pad_right(
                    self.map_arg(a, node.args.defaults[i - len(node.args.defaults)] if i >= first_with_default else None),
                    self.__source_before(',')) for i, a in enumerate(node.args.args)]
            ),
            self.__source_before(':'),
            self.__convert(node.body),
            self.__map_type(node)
        )

    def visit_List(self, node):
        prefix = self.__source_before('[')
        elements = JContainer(
            Space.EMPTY,
            [self.__pad_list_element(self.__convert(e), last=i == len(node.elts) - 1) for i, e in
             enumerate(node.elts)] if node.elts else
            [self.__pad_right(j.Empty(random_id(), self.__whitespace(), Markers.EMPTY), Space.EMPTY)],
            Markers.EMPTY
        )
        self.__skip(']')
        return py.CollectionLiteral(
            random_id(),
            prefix,
            Markers.EMPTY,
            py.CollectionLiteral.Kind.LIST,
            elements,
            self.__map_type(node)
        )

    def visit_ListComp(self, node):
        prefix = self.__source_before('[')
        result = self.__convert(node.elt)
        self.__skip('for')
        return py.ComprehensionExpression(
            random_id(),
            prefix,
            Markers.EMPTY,
            py.ComprehensionExpression.Kind.LIST,
            result,
            cast(List[py.ComprehensionExpression.Clause], [self.__convert(g) for g in node.generators]),
            self.__source_before(']'),
            self.__map_type(node)
        )

    def visit_comprehension(self, node):
        return py.ComprehensionExpression.Clause(
            random_id(),
            self.__source_before('for'),
            Markers.EMPTY,
            self.__convert(node.target),
            self.__pad_left(self.__source_before('in'), self.__convert(node.iter)),
            [self._map_comprehension_condition(i) for i in node.ifs] if node.ifs else []
        )

    def _map_comprehension_condition(self, i):
        return py.ComprehensionExpression.Condition(
            random_id(),
            self.__source_before('if'),
            Markers.EMPTY,
            self.__convert(i)
        )

    def visit_Module(self, node: ast.Module) -> py.CompilationUnit:
        return py.CompilationUnit(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            Path("TODO"),
            None,
            None,
            False,
            None,
            [],
            [self.__pad_statement(stmt) for stmt in node.body] if node.body else [
                self.__pad_right(j.Empty(random_id(), Space.EMPTY, Markers.EMPTY), Space.EMPTY)],
            self.__whitespace()
        )

    def visit_Name(self, node):
        return j.Identifier(
            random_id(),
            self.__source_before(node.id),
            Markers.EMPTY,
            [],
            node.id,
            self.__map_type(node),
            None
        )

    def visit_Return(self, node):
        return j.Return(
            random_id(),
            self.__source_before('return'),
            Markers.EMPTY,
            self.__convert(node.value) if node.value else None
        )

    def visit_Set(self, node):
        prefix = self.__source_before('{')
        elements = JContainer(
            Space.EMPTY,
            [self.__pad_list_element(self.__convert(e), last=i == len(node.elts) - 1) for i, e in enumerate(node.elts)] if node.elts else
            [self.__pad_right(j.Empty(random_id(), self.__whitespace(), Markers.EMPTY), Space.EMPTY)],
            Markers.EMPTY
        )
        self.__skip('}')
        return py.CollectionLiteral(
            random_id(),
            prefix,
            Markers.EMPTY,
            py.CollectionLiteral.Kind.SET,
            elements,
            self.__map_type(node)
        )

    def visit_SetComp(self, node):
        prefix = self.__source_before('{')
        result = self.__convert(node.elt)
        self.__skip('for')
        return py.ComprehensionExpression(
            random_id(),
            prefix,
            Markers.EMPTY,
            py.ComprehensionExpression.Kind.SET,
            result,
            cast(List[py.ComprehensionExpression.Clause], [self.__convert(g) for g in node.generators]),
            self.__source_before('}'),
            self.__map_type(node)
        )

    def visit_Slice(self, node):
        prefix = self.__whitespace()
        if node.lower:
            lower = self.__pad_right(self.__convert(node.lower), self.__source_before(':'))
        else:
            lower = self.__pad_right(j.Empty(random_id(), Space.EMPTY, Markers.EMPTY), self.__source_before(':'))
        upper = self.__pad_right(self.__convert(node.upper) if node.upper else j.Empty(random_id(), Space.EMPTY, Markers.EMPTY), self.__source_before(':') if node.step else self.__whitespace('\n'))
        step = self.__pad_right(self.__convert(node.step), self.__whitespace('\n')) if node.step else None
        return py.SliceExpression(
            random_id(),
            prefix,
            Markers.EMPTY,
            lower,
            upper,
            step
        )

    def visit_Starred(self, node):
        return py.StarExpression(
            random_id(),
            self.__source_before('*'),
            Markers.EMPTY,
            py.StarExpression.Kind.LIST,
            self.__convert(node.value),
            self.__map_type(node),
        )

    def visit_Subscript(self, node):
        return j.ArrayAccess(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            self.__convert(node.value),
            j.ArrayDimension(
                random_id(),
                self.__source_before('['),
                Markers.EMPTY,
                self.__pad_right(self.__convert(node.slice), self.__source_before(']'))
            ),
            self.__map_type(node)
        )

    def visit_Tuple(self, node):
        prefix = self.__source_before('(')
        elements = JContainer(
            Space.EMPTY,
            [self.__pad_list_element(self.__convert(e), last=i == len(node.elts) - 1) for i, e in enumerate(node.elts)] if node.elts else
            [self.__pad_right(j.Empty(random_id(), self.__whitespace(), Markers.EMPTY), Space.EMPTY)],
            Markers.EMPTY
        )
        self.__skip(')')
        return py.CollectionLiteral(
            random_id(),
            prefix,
            Markers.EMPTY,
            py.CollectionLiteral.Kind.TUPLE,
            elements,
            self.__map_type(node)
        )

    def visit_UnaryOp(self, node):
        mapped = self._map_unary_operator(node.op)
        return j.Unary(
            random_id(),
            self.__source_before(mapped[1]),
            Markers.EMPTY,
            self.__pad_left(Space.EMPTY, mapped[0]),
            self.__convert(node.operand),
            self.__map_type(node)
        )

    def __convert(self, node) -> Optional[J]:
        if node:
            if isinstance(node, ast.expr) and not isinstance(node, ast.Tuple):
                save_cursor = self._cursor
                prefix = self.__whitespace()
                if self._cursor < len(self._source) and self._source[self._cursor] == '(':
                    self._cursor += 1
                    self._parentheses_stack.append((lambda e, r: j.Parentheses(
                        random_id(),
                        prefix,
                        Markers.EMPTY,
                        self.__pad_right(e, r)
                    ), (node.lineno, node.col_offset)))
                    # handle nested parens
                    result = self.__convert(node)
                else:
                    self._cursor = save_cursor
                    result = self.visit(node)

                save_cursor = self._cursor
                suffix = self.__whitespace()
                if len(self._parentheses_stack) > 0 and self._cursor < len(self._source) and self._source[
                    self._cursor] == ')' and self._parentheses_stack[-1][1] == (node.lineno, node.col_offset):
                    self._cursor += 1
                    result = self._parentheses_stack.pop()[0](result, suffix)
                else:
                    self._cursor = save_cursor
                return result
            else:
                return self.visit(node)
        else:
            return None

    def __pad_statement(self, stmt: ast.stmt) -> JRightPadded[Statement]:
        statement = self.__convert(stmt)
        # use whitespace until end of line as padding; what follows will be prefix of next element
        padding = self.__whitespace('\n')
        if self._cursor < len(self._source) and self._source[self._cursor] == ';':
            self._cursor += 1
            markers = Markers.EMPTY.with_markers([Semicolon(random_id())])
        else:
            markers = Markers.EMPTY
        return JRightPadded(statement, padding, markers)

    def __pad_list_element(self, element: J, last: bool = False) -> JRightPadded[J]:
        padding = self.__whitespace()
        markers = Markers.EMPTY
        if last and self._source[self._cursor] == ',':
            self._cursor += 1
            markers = markers.with_markers([TrailingComma(random_id(), self.__whitespace('\n'))])
        elif not last:
            self._cursor += 1
            markers = Markers.EMPTY
        return JRightPadded(element, padding, markers)

    def __pad_right(self, tree, space: Space) -> JRightPadded[J2]:
        return JRightPadded(tree, space, Markers.EMPTY)

    def __pad_left(self, space: Space, tree) -> JLeftPadded[J2]:
        return JLeftPadded(space, tree, Markers.EMPTY)

    def __source_before(self, until_delim: str, stop: Optional[str] = None) -> Space:
        delim_index = self.__position_of_next(until_delim, stop)
        if delim_index == -1:
            return Space.EMPTY

        if delim_index == self._cursor:
            self._cursor = self._cursor + len(until_delim)
            return Space.EMPTY

        space = self.__whitespace()
        self._cursor = delim_index + len(until_delim)
        return space

    def __skip(self, token: Optional[str]) -> Optional[str]:
        if token is None:
            return None
        if self._source.startswith(token, self._cursor):
            self._cursor += len(token)
        return token

    def __whitespace(self, stop: str = None) -> Space:
        prefix = None
        whitespace = []
        comments = []
        source_len = len(self._source)
        while self._cursor < source_len:
            char = self._source[self._cursor]
            if stop is not None and char == stop:
                break
            if char.isspace() or char == '\\':
                whitespace.append(char)
            elif char == '#':
                if comments:
                    comments[-1] = comments[-1].with_suffix('\n' + ''.join(whitespace))
                else:
                    prefix = ''.join(whitespace)
                whitespace = []
                comment = []
                while self._cursor < source_len and self._source[self._cursor] != '\n':
                    comment.append(self._source[self._cursor])
                    self._cursor += 1
                comments.append(TextComment(False, ''.join(comment), '\n' if self._cursor < source_len else '',
                                            Markers.EMPTY))
            else:
                break
            self._cursor += 1

        if not comments:
            prefix = ''.join(whitespace)
        elif whitespace:
            comments[-1] = comments[-1].with_suffix('\n' + ''.join(whitespace))
        return Space(comments, prefix)

    def __position_of_next(self, until_delim: str, stop: str = None) -> int:
        in_single_line_comment = False

        delim_index = self._cursor
        while delim_index < len(self._source) - len(until_delim) + 1:
            if in_single_line_comment:
                if self._source[delim_index] == '\n':
                    in_single_line_comment = False
            else:
                if self._source[delim_index] == '#':
                    in_single_line_comment = True

            if not in_single_line_comment:
                if stop is not None and self._source[delim_index] == stop:
                    return -1  # reached stop word before finding the delimiter

                if self._source.startswith(until_delim, delim_index):
                    break  # found it!

            delim_index += 1

        return -1 if delim_index > len(self._source) - len(until_delim) else delim_index

    def __map_type(self, node) -> Optional[JavaType]:
        return None

    def _map_unary_operator(self, op) -> Tuple[j.Unary.Type, str]:
        operation_map: Dict[Type[ast], Tuple[j.Unary.Type, str]] = {
            ast.Invert: (j.Unary.Type.Complement, '~'),
            ast.Not: (j.Unary.Type.Not, 'not'),
            ast.UAdd: (j.Unary.Type.Positive, '+'),
            ast.USub: (j.Unary.Type.Negative, '-'),
        }
        return operation_map[type(op)]

    def _map_assignment_operator(self, op):
        operation_map: Dict[Type[ast], Tuple[j.AssignmentOperation.Type, str]] = {
            ast.Add: (j.AssignmentOperation.Type.Addition, '+='),
            ast.BitAnd: (j.AssignmentOperation.Type.BitAnd, '&='),
            ast.BitOr: (j.AssignmentOperation.Type.BitOr, '|='),
            ast.BitXor: (j.AssignmentOperation.Type.BitXor, '^='),
            ast.Div: (j.AssignmentOperation.Type.Division, '/='),
            ast.Pow: (j.AssignmentOperation.Type.Exponentiation, '**='),
            ast.FloorDiv: (j.AssignmentOperation.Type.FloorDivision, '//='),
            ast.LShift: (j.AssignmentOperation.Type.LeftShift, '<<='),
            ast.MatMult: (j.AssignmentOperation.Type.MatrixMultiplication, '@='),
            ast.Mod: (j.AssignmentOperation.Type.Modulo, '%='),
            ast.Mult: (j.AssignmentOperation.Type.Multiplication, '*='),
            ast.RShift: (j.AssignmentOperation.Type.RightShift, '>>='),
            ast.Sub: (j.AssignmentOperation.Type.Subtraction, '-='),
        }
        try:
            op, op_str = operation_map[type(op)]
        except KeyError:
            raise ValueError(f"Unsupported operator: {op}")
        return self.__pad_left(self.__source_before(op_str), op)
