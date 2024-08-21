import ast
from _ast import AST
from io import BytesIO
from pathlib import Path
from tokenize import tokenize
from typing import Optional, TypeVar, cast, Callable, List, Tuple, Dict, Type

from rewrite import random_id
from rewrite.java import Space, JRightPadded, JContainer, JLeftPadded, JavaType, Markers, TextComment, J
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

    def visit_arguments(self, node):
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

    def _map_binary_operator(self, op) -> JLeftPadded[j.Binary.Type]:
        operation_map: Dict[Type[ast], Tuple[j.Binary.Type, str]] = {
            ast.Add: (j.Binary.Type.Addition, '+'),
            ast.And: (j.Binary.Type.And, 'and'),
            ast.Div: (j.Binary.Type.Division, '/'),
            ast.Mod: (j.Binary.Type.Modulo, '%'),
            ast.Mult: (j.Binary.Type.Multiplication, '*'),
            ast.Or: (j.Binary.Type.Or, 'or'),
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
        next(tokens) # skip ENCODING token
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
            [self.__pad_right(self.__convert(cast(AST, stmt)), Space.EMPTY) for stmt in node.body] if node.body else [
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

    def visit_List(self, node):
        prefix = self.__source_before('[')
        elements = JContainer(Space.EMPTY, [self.__pad_right(self.__convert(e), self.__source_before(',')) for e in node.elts],
                              Markers.EMPTY)
        self.__skip(']')
        return j.NewArray(
            random_id(),
            prefix,
            Markers.EMPTY,
            None,
            [],
            elements,
            self.__map_type(node)
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
            [self.__pad_right(self.visit(cast(AST, stmt)), self.__whitespace()) for stmt in
             node.body] if node.body else [
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

    def __convert(self, node) -> Optional[J]:
        if node:
            if isinstance(node, ast.expr):
                save_cursor = self._cursor
                prefix = self.__whitespace()
                if self._source[self._cursor] == '(':
                    self._cursor += 1
                    self._parentheses_stack.append((lambda e, r: j.Parentheses(
                        random_id(),
                        prefix,
                        Markers.EMPTY,
                        self.__pad_right(e, r)
                    ), (node.lineno,node.col_offset)))
                    # handle nested parens
                    result = self.__convert(node)
                else:
                    self._cursor = save_cursor
                    result = self.visit(node)

                save_cursor = self._cursor
                suffix = self.__whitespace()
                if len(self._parentheses_stack) > 0 and self._cursor < len(self._source) and self._source[self._cursor] == ')' and self._parentheses_stack[-1][1] == (node.lineno, node.col_offset):
                    self._cursor += 1
                    result = self._parentheses_stack.pop()[0](result, suffix)
                else:
                    self._cursor = save_cursor
                return result
            else:
                return self.visit(node)
        else:
            return None

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

    def __whitespace(self) -> Space:
        prefix = None
        whitespace = []
        comments = []
        while self._cursor < len(self._source):
            char = self._source[self._cursor]
            if char.isspace() or char == '\\':
                whitespace.append(char)
            elif char == '#':
                if comments:
                    comments[-1] = comments[-1].with_suffix('\n' + ''.join(whitespace))
                else:
                    prefix = ''.join(whitespace)
                whitespace = []
                comment = []
                while self._cursor < len(self._source) and self._source[self._cursor] != '\n':
                    comment.append(self._source[self._cursor])
                    self._cursor += 1
                comments.append(TextComment(False, ''.join(comment), '\n' if self._cursor < len(self._source) else '',
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
