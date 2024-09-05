import ast
import sys
import token
from argparse import ArgumentError
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from tokenize import tokenize, TokenInfo
from typing import Optional, TypeVar, cast, Callable, List, Tuple, Dict, Type, Sequence, Union

from more_itertools import peekable

from rewrite import random_id, Markers
from rewrite.java import Space, JRightPadded, JContainer, JLeftPadded, JavaType, J, Statement, Semicolon, TrailingComma, \
    NameTree, OmitParentheses, Expression
from rewrite.java import tree as j
from . import tree as py, PyComment
from .markers import KeywordArguments, KeywordOnlyArguments

J2 = TypeVar('J2', bound=J)


class ParserVisitor(ast.NodeVisitor):

    _source: str
    _cursor: int
    _parentheses_stack: List[Tuple[Callable[[J, Space], j.Parentheses], int]]

    @property
    def _source_after_cursor(self) -> str:
        return self._slow_source_after_cursor(self._source, self._cursor)

    @staticmethod
    @lru_cache
    def _slow_source_after_cursor(source: str, cursor: int) -> str:
        return source[cursor:]

    def __init__(self, source: str):
        super().__init__()
        self._source = source
        self._cursor = 0
        self._parentheses_stack = []

    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_arguments(self, node) -> JContainer[j.VariableDeclarations]:
        first_with_default = len(node.args) - len(node.defaults) if node.defaults else sys.maxsize
        prefix = self.__source_before('(')
        if not node.args and not node.vararg and not node.kwarg and not node.kwonlyargs:
            return JContainer(prefix, [
                JRightPadded(j.Empty(random_id(), self.__source_before(')'), Markers.EMPTY), Space.EMPTY,
                             Markers.EMPTY)], Markers.EMPTY)

        args = [self.__pad_list_element(
            self.map_arg(a, node.defaults[i - first_with_default] if i >= first_with_default else None),
            i == len(node.args) - 1,
            end_delim=',' if node.vararg or node.kwarg or node.kwonlyargs else ')') for i, a in enumerate(node.args)]
        if node.vararg:
            args.append(self.__pad_list_element(
                self.map_arg(node.vararg, None, vararg=True),
                not node.kwarg and not node.kwonlyargs,
                end_delim=')'
            ))
        if node.kwarg:
            args.append(self.__pad_list_element(
                self.map_arg(node.kwarg, None, kwarg=True),
                not node.kwonlyargs,
                end_delim=')'
            ))
        if node.kwonlyargs:
            empty_name = j.VariableDeclarations.NamedVariable(random_id(), Space.EMPTY, Markers.EMPTY,
                                                              cast(j.Identifier, self.__convert_name('', None)), [],
                                                              None, None, None)
            kwonly_prefix = self.__source_before('*')
            kwonlyargs = [self.__pad_right(empty_name, self.__source_before(','))]
            for i, kwonlyarg in enumerate(node.kwonlyargs):
                kwonlyargs.append(self.__pad_list_element(j.VariableDeclarations.NamedVariable(
                    random_id(),
                    self.__whitespace(),
                    Markers.EMPTY,
                    cast(j.Identifier, self.__convert_name(kwonlyarg.arg)),
                    [], None, None, None
                ), last=i == len(node.kwonlyargs) - 1))
            args.append(self.__pad_right(j.VariableDeclarations(
                random_id(),
                kwonly_prefix,
                Markers(random_id(), [KeywordOnlyArguments(random_id())]),
                [], [], None, None, [],
                kwonlyargs,
                None
            ), self.__source_before(')')))
        return JContainer(prefix, args, Markers.EMPTY)


    def map_arg(self, node, default=None, vararg=False, kwarg=False):
        prefix = self.__source_before('**') if kwarg else self.__whitespace()
        vararg_prefix = self.__source_before('*') if vararg else None
        name = self.__convert_name(node.arg, self.__map_type(node))
        after_name = self.__source_before(':') if node.annotation else Space.EMPTY
        type_expression = self.__convert(node.annotation) if node.annotation else None
        initializer = self.__pad_left(self.__source_before('='), self.__convert(default)) if default else None

        return j.VariableDeclarations(
            random_id(),
            prefix,
            Markers(random_id(), [KeywordArguments(random_id())]) if kwarg else Markers.EMPTY,
            [],
            [],
            type_expression,
            vararg_prefix if vararg else None,
            [],
            [self.__pad_right(j.VariableDeclarations.NamedVariable(
                random_id(),
                Space.EMPTY,
                Markers.EMPTY,
                cast(j.Identifier, name),
                [],
                initializer,
                self.__map_type(node)
            ), after_name)],
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
        if len(node.targets) == 1:
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
        return py.Await(
            random_id(),
            self.__source_before('await'),
            Markers.EMPTY,
            self.__convert(node.value),
            self.__map_type(node)
        )


    def visit_Interactive(self, node):
        raise NotImplementedError("Implement visit_Interactive!")


    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)


    def visit_ClassDef(self, node):
        prefix = self.__whitespace() if node.decorator_list else Space.EMPTY
        decorators = [self.__map_decorator(d) for d in node.decorator_list]
        kind_prefix = self.__source_before('class')
        name = self.__convert_name(node.name)
        save_cursor = self._cursor
        interfaces_prefix = self.__whitespace()
        if self._source[self._cursor] == '(' and node.bases:
            self.__skip('(')
            interfaces = JContainer(
                interfaces_prefix,
                [
                    self.__pad_list_element(self.__convert(n), i == len(node.bases) - 1, end_delim=')') for i, n in
                    enumerate(node.bases)],
                Markers.EMPTY
            )
        elif self._source[self._cursor] == '(':
            self.__skip('(')
            interfaces = JContainer(
                interfaces_prefix,
                [self.__pad_right(j.Empty(random_id(), self.__source_before(')'), Markers.EMPTY), Space.EMPTY)],
                Markers.EMPTY
            )
        else:
            interfaces = None
            self._cursor = save_cursor
        return j.ClassDeclaration(
            random_id(),
            prefix,
            Markers.EMPTY,
            decorators,
            [],  # TODO modifiers
            j.ClassDeclaration.Kind(
                random_id(),
                kind_prefix,
                Markers.EMPTY,
                [],
                j.ClassDeclaration.Kind.Type.Class
            ),
            name,
            None,
            None,
            None,  # no `extends`, all in `implements`
            interfaces,
            None,
            self.__convert_block(node.body),
            self.__map_type(node)
        )


    def visit_Delete(self, node):
        return py.Del(
            random_id(),
            self.__source_before('del'),
            Markers.EMPTY,
            [self.__pad_list_element(self.__convert(e), last=i == len(node.targets) - 1) for i, e in
             enumerate(node.targets)]
        )


    def visit_AnnAssign(self, node):
        prefix = self.__whitespace()
        name = self.__convert(node.target)
        after_name = self.__source_before(':') if node.annotation else Space.EMPTY
        var_type = self.__convert(node.annotation)
        initializer = self.__pad_left(
            self.__source_before('='),
            self.__convert(node.value)
        ) if node.value else None

        return j.VariableDeclarations(
            random_id(),
            prefix,
            Markers.EMPTY,
            [],
            [],
            var_type,
            None,
            [],
            [self.__pad_right(
                j.VariableDeclarations.NamedVariable(
                    random_id(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    name,
                    [],
                    initializer,
                    self.__map_type(node.target)),
                after_name
            )]
        )


    def visit_For(self, node):
        targets = node.target.elts if isinstance(node.target, ast.Tuple) else [node.target]
        return j.ForEachLoop(
            random_id(),
            self.__source_before('for'),
            Markers.EMPTY,
            j.ForEachLoop.Control(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                self.__pad_right(
                    j.VariableDeclarations(
                        random_id(),
                        Space.EMPTY,
                        Markers.EMPTY,
                        [],
                        [],
                        None,
                        None,
                        [],
                        [self.__pad_list_element(
                            j.VariableDeclarations.NamedVariable(
                                random_id(),
                                Space.EMPTY,
                                Markers.EMPTY,
                                self.__convert(t),
                                [],
                                None,
                                self.__map_type(t)
                            ),
                            i == len(targets) - 1,
                            False
                        ) for i, t in enumerate(targets)]
                    ),
                    self.__source_before('in')
                ),
                self.__pad_right(self.__convert(node.iter), Space.EMPTY),
            ),
            self.__pad_right(self.__convert_block(node.body), Space.EMPTY)
        )


    def visit_AsyncFor(self, node):
        raise NotImplementedError("Implement visit_AsyncFor!")


    def visit_While(self, node):
        return j.WhileLoop(
            random_id(),
            self.__source_before('while'),
            Markers.EMPTY,
            j.ControlParentheses(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                self.__pad_right(self.__convert(node.test), Space.EMPTY)
            ),
            self.__pad_right(self.__convert_block(node.body), Space.EMPTY)
        )


    def visit_If(self, node):
        prefix = self.__source_before('if')
        single_statement_then_body = len(node.body) == 1
        condition = j.ControlParentheses(random_id(), self.__whitespace(), Markers.EMPTY,
                                         self.__pad_right(self.__convert(node.test), self.__source_before(
                                             ':') if single_statement_then_body else Space.EMPTY))
        then = self.__pad_right(
            self.__convert(node.body[0]) if single_statement_then_body else self.__convert_block(node.body), Space.EMPTY)
        elze = None
        if len(node.orelse) > 0:
            else_prefix = self.__whitespace()
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If) and self._source.startswith('elif', self._cursor):
                single_statement_else_body = True
                self._cursor += 2
            else:
                single_statement_else_body = False
                self._cursor += 4

            elze = j.If.Else(
                random_id(),
                else_prefix,
                Markers.EMPTY,
                self.__pad_right(
                    self.__convert(node.orelse[0]) if single_statement_else_body else self.__convert_block(node.orelse),
                    Space.EMPTY
                )
            )
        return j.If(
            random_id(),
            prefix,
            Markers.EMPTY,
            condition,
            then,
            elze
        )


    def visit_With(self, node):
        return j.Try(
            random_id(),
            self.__source_before('with'),
            Markers.EMPTY,
            JContainer(
                self.__whitespace(),
                [self.__pad_list_element(self.__convert(r), i == len(node.items) - 1) for i, r in
                 enumerate(node.items)],
                Markers.EMPTY
            ),
            self.__convert_block(node.body),
            [],
            None
        )


    def visit_withitem(self, node):
        prefix = self.__whitespace()
        expr = self.__convert(node.context_expr)
        value = self.__pad_left(self.__source_before('as'), expr)
        name = self.__convert(node.optional_vars)
        return j.Try.Resource(
            random_id(),
            prefix,
            Markers.EMPTY,
            j.Assignment(
                random_id(),
                Space.EMPTY,
                Markers.EMPTY,
                name,
                value,
                self.__map_type(node.context_expr)
            ),
            False
        )


    def visit_AsyncWith(self, node):
        raise NotImplementedError("Implement visit_AsyncWith!")


    def visit_Raise(self, node):
        return py.Throw(
            random_id(),
            self.__source_before('raise'),
            Markers.EMPTY,
            self.__convert(node.exc),
        )


    def visit_Try(self, node):
        return j.Try(
            random_id(),
            self.__source_before('try'),
            Markers.EMPTY,
            JContainer.empty(),
            self.__convert_block(node.body),
            [self.__convert(handler) for handler in node.handlers],
            self.__pad_left(self.__source_before('finally'),
                            self.__convert_block(node.finalbody)) if node.finalbody else None
        )


    def visit_Import(self, node):
        # TODO only use `MultiImport` when necessary (requires corresponding changes to printer)
        return py.MultiImport(
            random_id(),
            self.__source_before('import'),
            Markers.EMPTY,
            None,
            False,
            JContainer(
                Space.EMPTY,
                [self.__pad_list_element(self.__convert(n), i == len(node.names) - 1) for i, n in
                 enumerate(node.names)],
                Markers.EMPTY
            )
        )


    def visit_ImportFrom(self, node):
        prefix = self.__source_before('from')
        from_ = self.__pad_right(self.__convert_name(('.' * node.level) + (node.module if node.module else '')),
                                 self.__source_before('import'))
        names_prefix = self.__whitespace()
        if parenthesized := self._source[self._cursor] == '(':
            self.__skip('(')
        multi_import = py.MultiImport(
            random_id(),
            prefix,
            Markers.EMPTY,
            from_,
            parenthesized,
            JContainer(
                names_prefix,
                [self.__pad_list_element(self.__convert(n), i == len(node.names) - 1) for i, n in
                 enumerate(node.names)],
                Markers.EMPTY
            )
        )
        if parenthesized:
            self.__skip(')')
        return multi_import


    def visit_alias(self, node):
        return j.Import(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            self.__pad_left(Space.EMPTY, False),
            self.__convert_qualified_name(node.name),
            None if not node.asname else
            self.__pad_left(self.__source_before('as'), self.__convert_name(node.asname))
        )


    def visit_keyword(self, node):
        if node.arg:
            return py.NamedArgument(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                self.__convert_name(node.arg),
                self.__pad_left(self.__source_before('='), self.__convert(node.value)),
                self.__map_type(node)

            )
        prefix = self.__whitespace()
        if self._source.startswith('**', self._cursor):
            self.__skip('**')
            return py.Star(
                random_id(),
                prefix,
                Markers.EMPTY,
                py.Star.Kind.DICT,
                self.__convert(node.value),
                self.__map_type(node.value),
            )

    def __convert_qualified_name(self, name: str) -> j.FieldAccess:
        if '.' not in name:
            return j.FieldAccess(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                j.Empty(random_id(), Space.EMPTY, Markers.EMPTY),
                self.__pad_left(
                    Space.EMPTY,
                    self.__convert_name(name)
                ),
                None
            )
        return cast(j.FieldAccess, self.__convert_name(name))


    def visit_Global(self, node):
        raise NotImplementedError("Implement visit_Global!")


    def visit_Nonlocal(self, node):
        raise NotImplementedError("Implement visit_Nonlocal!")


    def visit_Pass(self, node):
        return py.Pass(
            random_id(),
            self.__source_before('pass'),
            Markers.EMPTY,
        )


    def visit_Break(self, node):
        return j.Break(random_id(), self.__source_before('break'), Markers.EMPTY, None)


    def visit_Continue(self, node):
        return j.Continue(random_id(), self.__source_before('continue'), Markers.EMPTY, None)


    def visit_GeneratorExp(self, node):
        # this weird logic is here to deal with the case of generator expressions appearing as the argument to a call
        prefix = self.__whitespace()
        if self._source[self._cursor] == '(':
            save_cursor = self._cursor
            self._cursor += 1
            try:
                result = self.__convert(node.elt)
                save_cursor_2 = self._cursor
                self.__whitespace()
                assert self._source[self._cursor] != ')'
                self._cursor = save_cursor_2
                parenthesized = True
            except:
                self._cursor = save_cursor
                result = self.__convert(node.elt)
                parenthesized = False
        else:
            result = self.__convert(node.elt)
            parenthesized = False

        return py.ComprehensionExpression(
            random_id(),
            prefix,
            Markers.EMPTY if parenthesized else Markers.EMPTY.with_markers([OmitParentheses(random_id())]),
            py.ComprehensionExpression.Kind.GENERATOR,
            result,
            cast(List[py.ComprehensionExpression.Clause], [self.__convert(g) for g in node.generators]),
            self.__source_before(')') if parenthesized else Space.EMPTY,
            self.__map_type(node)
        )


    def visit_Expr(self, node):
        return py.ExpressionStatement(
            random_id(),
            self.__convert(node.value)
        )


    def visit_Yield(self, node):
        return py.StatementExpression(
            random_id(),
            j.Yield(
                random_id(),
                self.__source_before('yield'),
                Markers.EMPTY,
                False,
                self.__convert(node.value),
            )
        )


    def visit_YieldFrom(self, node):
        return py.StatementExpression(
            random_id(),
            j.Yield(
                random_id(),
                self.__source_before('yield'),
                Markers.EMPTY,
                False,
                py.YieldFrom(
                    random_id(),
                    self.__source_before('from'),
                    Markers.EMPTY,
                    self.__convert(node.value),
                    self.__map_type(node)
                )
            )
        )


    def visit_TypeIgnore(self, node):
        raise NotImplementedError("Implement visit_TypeIgnore!")


    def visit_Attribute(self, node):
        return j.FieldAccess(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            self.__convert(node.value),
            self.__pad_left(self.__source_before('.'), self.__convert_name(node.attr)),
            self.__map_type(node),
        )


    def visit_Del(self, node):
        raise NotImplementedError("Implement visit_Del!")


    def visit_Load(self, node):
        raise NotImplementedError("Implement visit_Load!")


    def visit_Store(self, node):
        raise NotImplementedError("Implement visit_Store!")


    def visit_ExceptHandler(self, node):
        prefix = self.__source_before('except')
        except_type = self.__convert(node.type) if node.type else j.Empty(random_id(), Space.EMPTY, Markers.EMPTY)
        if node.name:
            before_as = self.__source_before('as')
            except_type_name = self.__convert_name(node.name)
        else:
            before_as = Space.EMPTY
            except_type_name = j.Identifier(random_id(), Space.EMPTY, Markers.EMPTY, [], '', None, None)
        except_type_name = self.__pad_right(
            j.VariableDeclarations.NamedVariable(
                random_id(),
                Space.EMPTY,
                Markers.EMPTY,
                except_type_name,
                [], None, None
            ),
            before_as
        )

        return j.Try.Catch(
            random_id(),
            prefix,
            Markers.EMPTY,
            j.ControlParentheses(
                random_id(),
                Space.EMPTY,
                Markers.EMPTY,
                self.__pad_right(j.VariableDeclarations(
                    random_id(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    [], [],
                    except_type,
                    None, [],
                    [except_type_name]
                ), Space.EMPTY)
            ),
            self.__convert_block(node.body)
        )


    def visit_Match(self, node):
        return j.Switch(
            random_id(),
            self.__source_before('match'),
            Markers.EMPTY,
            j.ControlParentheses(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                self.__pad_right(self.__convert(node.subject), Space.EMPTY)
            ),
            self.__convert_block(node.cases)
        )


    def visit_match_case(self, node):
        prefix = self.__source_before('case')
        pattern_prefix = self.__whitespace()

        pattern = self.__convert(node.pattern)
        # if isinstance(pattern, py.MatchCase):
        #     guard = self.__pad_left(self.__source_before('if'), self.__convert(node.guard))
        #     pattern = pattern.padding.with_guard(guard)

        case = j.Case(
            random_id(),
            prefix,
            Markers.EMPTY,
            j.Case.Type.Rule,
            JContainer(
                pattern_prefix,
                [self.__pad_right(pattern, Space.EMPTY)],
                Markers.EMPTY
            ),
            JContainer.empty(),
            self.__pad_right(self.__convert_block(node.body), Space.EMPTY)
        )
        return case


    def visit_MatchValue(self, node):
        return self.__convert(node.value)


    def visit_MatchSequence(self, node):
        prefix = self.__whitespace()
        end_delim = None
        if self._source[self._cursor] == '[':
            kind = py.MatchCase.Pattern.Kind.SEQUENCE_LIST
            self._cursor += 1
            end_delim = ']'
        elif self._source[self._cursor] == '(':
            kind = py.MatchCase.Pattern.Kind.SEQUENCE_TUPLE
            self._cursor += 1
            end_delim = ')'
        else:
            kind = py.MatchCase.Pattern.Kind.SEQUENCE
        return py.MatchCase(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            py.MatchCase.Pattern(
                random_id(),
                Space.EMPTY,
                Markers.EMPTY,
                kind,
                JContainer(
                    prefix,
                    [self.__pad_list_element(self.__convert(e), last=i == len(node.patterns) - 1,
                                             end_delim=end_delim) for i, e in
                     enumerate(node.patterns)] if node.patterns else [],
                    Markers.EMPTY
                ),
                None
            ),
            None,
            None
        )


    def visit_MatchSingleton(self, node):
        raise NotImplementedError("Implement visit_MatchSingleton!")


    def visit_MatchStar(self, node):
        return py.Star(
            random_id(),
            self.__source_before('*'),
            Markers.EMPTY,
            py.Star.Kind.LIST,
            self.__convert_name(node.name),
            None
        )


    def visit_MatchMapping(self, node):
        raise NotImplementedError("Implement visit_MatchMapping!")


    def visit_MatchClass(self, node):
        prefix = self.__whitespace()
        children = [self.__pad_right(self.__convert(node.cls), self.__source_before('('))]
        if len(node.patterns) > 0:
            for i, arg in enumerate(node.patterns):
                arg_name = j.VariableDeclarations(
                    random_id(),
                    self.__whitespace(),
                    Markers.EMPTY,
                    [], [], None, None, [],
                    [
                        self.__pad_right(j.VariableDeclarations.NamedVariable(
                            random_id(),
                            Space.EMPTY,
                            Markers.EMPTY,
                            cast(j.Identifier, self.__convert(arg)),
                            [],
                            None,
                            None
                        ), Space.EMPTY)
                    ]
                )
                converted = self.__pad_list_element(arg_name, last=i == len(node.patterns) - 1,
                                                    end_delim=')' if len(node.kwd_attrs) == 0 else ',')
                children.append(converted)
            for i, kwd in enumerate(node.kwd_attrs):
                kwd_var = j.VariableDeclarations(
                    random_id(),
                    self.__whitespace(),
                    Markers.EMPTY,
                    [], [], None, None, [],
                    [
                        self.__pad_right(j.VariableDeclarations.NamedVariable(
                            random_id(),
                            Space.EMPTY,
                            Markers.EMPTY,
                            cast(j.Identifier, self.__convert_name(kwd)),
                            [],
                            self.__pad_left(self.__source_before('='), self.__convert(node.kwd_patterns[i])),
                            None
                        ), Space.EMPTY)
                    ]
                )
                converted = self.__pad_list_element(kwd_var, last=i == len(node.kwd_attrs) - 1,
                                                    end_delim=')')
                children.append(converted)
        else:
            children.append(
                self.__pad_right(j.Empty(random_id(), self.__source_before(')'), Markers.EMPTY), Space.EMPTY))
        return py.MatchCase(
            random_id(),
            prefix,
            Markers.EMPTY,
            py.MatchCase.Pattern(
                random_id(),
                Space.EMPTY,
                Markers.EMPTY,
                py.MatchCase.Pattern.Kind.CLASS,
                JContainer(Space.EMPTY, children, Markers.EMPTY),
                None
            ),
            None,
            None
        )


    def visit_MatchAs(self, node):
        if node.name is None and node.pattern is None:
            return py.MatchCase(
                random_id(),
                self.__source_before('_'),
                Markers.EMPTY,
                py.MatchCase.Pattern(
                    random_id(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    py.MatchCase.Pattern.Kind.WILDCARD,
                    JContainer.empty(),
                    None
                ),
                None,
                None
            )
        elif node.name is not None and node.pattern is not None:
            return self.__convert_name(node.name)
        else:
            return py.MatchCase(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                py.MatchCase.Pattern(
                    random_id(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    py.MatchCase.Pattern.Kind.AS,
                    JContainer(
                        Space.EMPTY,
                        [
                            self.__pad_right(self.__convert(node.pattern), self.__source_before('as')),
                            self.__pad_right(self.__convert_name(node.name), Space.EMPTY),
                        ],
                        Markers.EMPTY
                    ),
                    None
                ),
                None,
                None
            )


    def visit_MatchOr(self, node):
        return py.MatchCase(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            py.MatchCase.Pattern(
                random_id(),
                Space.EMPTY,
                Markers.EMPTY,
                py.MatchCase.Pattern.Kind.OR,
                JContainer(
                    Space.EMPTY,
                    [self.__pad_list_element(self.__convert(e), last=i == len(node.patterns) - 1) for i, e in
                     enumerate(node.patterns)] if node.patterns else [],
                    Markers.EMPTY
                ),
                None
            ),
            None,
            None
        )


    def visit_TryStar(self, node):
        raise NotImplementedError("Implement visit_TryStar!")


    def visit_TypeVar(self, node):
        raise NotImplementedError("Implement visit_TypeVar!")


    def visit_ParamSpec(self, node):
        raise NotImplementedError("Implement visit_ParamSpec!")


    def visit_TypeVarTuple(self, node):
        raise NotImplementedError("Implement visit_TypeVarTuple!")


    def visit_TypeAlias(self, node):
        raise NotImplementedError("Implement visit_TypeAlias!")


    def visit_ExtSlice(self, node):
        raise NotImplementedError("Implement visit_ExtSlice!")


    def visit_Index(self, node):
        raise NotImplementedError("Implement visit_Index!")


    def visit_Suite(self, node):
        raise NotImplementedError("Implement visit_Suite!")


    def visit_AugLoad(self, node):
        raise NotImplementedError("Implement visit_AugLoad!")


    def visit_AugStore(self, node):
        raise NotImplementedError("Implement visit_AugStore!")


    def visit_Param(self, node):
        raise NotImplementedError("Implement visit_Param!")


    def visit_Num(self, node):
        raise NotImplementedError("Implement visit_Num!")


    def visit_Str(self, node):
        raise NotImplementedError("Implement visit_Str!")


    def visit_Bytes(self, node):
        raise NotImplementedError("Implement visit_Bytes!")


    def visit_NameConstant(self, node):
        raise NotImplementedError("Implement visit_NameConstant!")


    def visit_Ellipsis(self, node):
        raise NotImplementedError("Implement visit_Ellipsis!")


    def visit_BinOp(self, node):
        return j.Binary(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            self.__convert(node.left),
            self.__convert_binary_operator(node.op),
            self.__convert(node.right),
            self.__map_type(node)
        )


    def visit_BoolOp(self, node):
        binaries = []
        prefix = Space.EMPTY
        left = self.__convert(node.values[0])
        for right_expr in node.values[1:]:
            left = j.Binary(
                random_id(),
                prefix,
                Markers.EMPTY,
                left,
                self.__convert_binary_operator(node.op),
                self.__convert(right_expr),
                self.__map_type(node)
            )
            binaries.append(left)
            prefix = Space.EMPTY

        return binaries[-1]


    def visit_Call(self, node):
        prefix = self.__whitespace()
        if isinstance(node.func, ast.Name):
            select = None
            name = cast(j.Identifier, self.__convert(node.func))
        elif isinstance(node.func, ast.Call):
            select = self.__pad_right(cast(Expression, self.__convert(node.func)), self.__whitespace())
            # printer handles empty name by not printing `.` before it
            name = self.__convert_name('')
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
        else:
            raise NotImplementedError("Calls to functions other than methods are not yet supported")

        all_args = node.args + node.keywords
        args = JContainer(
            self.__source_before('('),
            [self.__pad_list_element(self.__convert(a), last=i == len(all_args) - 1, end_delim=')') for i, a in
             enumerate(all_args)] if all_args else [
                self.__pad_right(j.Empty(random_id(), self.__source_before(')'), Markers.EMPTY),
                                 Space.EMPTY)],
            Markers.EMPTY
        )

        return j.MethodInvocation(
            random_id(),
            prefix,
            Markers.EMPTY,
            select,
            None,
            name,
            args,
            self.__map_type(node)
        )


    def visit_Compare(self, node):
        if len(node.ops) != 1:
            raise NotImplementedError("Multiple comparisons are not yet supported")

        prefix = self.__whitespace()
        left = self.__convert(node.left)
        op = self.__convert_binary_operator(node.ops[0])

        if isinstance(op.element, j.Binary.Type):
            return j.Binary(
                random_id(),
                prefix,
                Markers.EMPTY,
                left,
                op,
                self.__convert(node.comparators[0]),
                self.__map_type(node)
            )
        else:
            if op.element == py.Binary.Type.IsNot:
                negation = self.__source_before('not')
            elif op.element == py.Binary.Type.NotIn:
                negation = self.__source_before('in')
            else:
                negation = None

            return py.Binary(
                random_id(),
                prefix,
                Markers.EMPTY,
                left,
                op,
                negation,
                self.__convert(node.comparators[0]),
                self.__map_type(node)
            )


    def __convert_binary_operator(self, op) -> Union[JLeftPadded[j.Binary.Type], JLeftPadded[py.Binary.Type]]:
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
            ast.In: (py.Binary.Type.In, 'in'),
            ast.Is: (py.Binary.Type.Is, 'is'),
            ast.IsNot: (py.Binary.Type.IsNot, 'is'),
            ast.LShift: (j.Binary.Type.LeftShift, '<<'),
            ast.Lt: (j.Binary.Type.LessThan, '<'),
            ast.LtE: (j.Binary.Type.LessThanOrEqual, '<='),
            ast.Mod: (j.Binary.Type.Modulo, '%'),
            ast.Mult: (j.Binary.Type.Multiplication, '*'),
            ast.NotEq: (j.Binary.Type.NotEqual, '!='),
            ast.NotIn: (py.Binary.Type.NotIn, 'not'),
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
        return j.Literal(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            None if node.value is Ellipsis else node.value,
            self.__next_lexer_token(),
            None,
            self.__map_type(node),
        )


    def visit_Dict(self, node):
        return py.DictLiteral(
            random_id(),
            self.__source_before('{'),
            Markers.EMPTY,
            JContainer(
                Space.EMPTY,
                [self.__pad_right(j.Empty(random_id(), self.__source_before('}'), Markers.EMPTY),
                                  Space.EMPTY)] if not node.keys else
                [self.__map_dict_entry(k, v, i == len(node.keys) - 1) for i, (k, v) in
                 enumerate(zip(node.keys, node.values))],
                Markers.EMPTY
            ),
            self.__map_type(node)
        )


    def visit_DictComp(self, node):
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


    def __map_dict_entry(self, key: Optional[ast.expr], value: ast.expr, last: bool) -> JRightPadded[J]:
        if key is None:
            element = py.Star(
                random_id(),
                self.__source_before('**'),
                Markers.EMPTY,
                py.Star.Kind.DICT,
                self.__convert(value),
                self.__map_type(value),
            )
        else:
            element = py.KeyValue(random_id(), self.__whitespace(), Markers.EMPTY,
                                  self.__pad_right(self.__convert(key), self.__source_before(':')),
                                  self.__convert(value),
                                  self.__map_type(value))
        return self.__pad_list_element(element, last, end_delim='}')


    def visit_FunctionDef(self, node: ast.FunctionDef) -> j.MethodDeclaration:
        decorators = [self.__map_decorator(d) for d in node.decorator_list]

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
        if node.returns is None:
            return_type = None
        else:
            return_type = py.TypeHint(
                random_id(),
                self.__source_before('->'),
                Markers.EMPTY,
                self.__convert(node.returns),
                self.__map_type(node.returns)
            )
        body = self.__convert_block(node.body)

        return j.MethodDeclaration(
            random_id(),
            Space.EMPTY,
            Markers.EMPTY,
            decorators,
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


    def __map_decorator(self, decorator) -> j.Annotation:
        prefix = self.__source_before('@')
        if isinstance(decorator, (ast.Attribute, ast.Name)):
            name = self.__convert(decorator)
            args = None
        elif isinstance(decorator, ast.Call):
            name = self.__convert(decorator.func)
            all_args = decorator.args + decorator.keywords
            args = JContainer(
                self.__source_before('('),
                [self.__pad_right(j.Empty(random_id(), self.__source_before(')'), Markers.EMPTY),
                                  Space.EMPTY)] if not all_args else
                [self.__pad_list_element(self.__convert(a), i == len(all_args) - 1, end_delim=')') for i, a in
                 enumerate(all_args)],
                Markers.EMPTY
            )
        else:
            raise NotImplementedError("Unsupported decorator type: " + str(type(decorator)))

        return j.Annotation(
            random_id(),
            prefix,
            Markers.EMPTY,
            name,
            args
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
        tok = next(tokens)  # FSTRING_START token
        return self.__map_fstring(node, prefix, tok, peekable(tokens))[0]


    def visit_FormattedValue(self, node):
        raise ValueError("This method should not be called directly")


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
                [self.__pad_list_element(
                    self.map_arg(a,
                                 node.args.defaults[
                                     i - len(node.args.defaults)] if i >= first_with_default else None),
                    i == len(node.args.args) - 1) for i, a in enumerate(node.args.args)]
            ),
            self.__source_before(':'),
            self.__convert(node.body),
            self.__map_type(node)
        )


    def visit_List(self, node):
        prefix = self.__source_before('[')
        elements = JContainer(
            Space.EMPTY,
            [self.__pad_list_element(self.__convert(e), last=i == len(node.elts) - 1, end_delim=']') for i, e in
             enumerate(node.elts)] if node.elts else
            [self.__pad_right(j.Empty(random_id(), self.__source_before(']'), Markers.EMPTY), Space.EMPTY)],
            Markers.EMPTY
        )
        return py.CollectionLiteral(
            random_id(),
            prefix,
            Markers.EMPTY,
            py.CollectionLiteral.Kind.LIST,
            elements,
            self.__map_type(node)
        )


    def visit_ListComp(self, node):
        return py.ComprehensionExpression(
            random_id(),
            self.__source_before('['),
            Markers.EMPTY,
            py.ComprehensionExpression.Kind.LIST,
            self.__convert(node.elt),
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
        cu = py.CompilationUnit(
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
        assert self._cursor == len(self._source)
        return cu


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


    def visit_NamedExpr(self, node):
        return j.Assignment(
            random_id(),
            self.__whitespace(),
            Markers.EMPTY,
            self.__convert(node.target),
            self.__pad_left(self.__source_before(':='), self.__convert(node.value)),
            self.__map_type(node.value)
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
            [self.__pad_list_element(self.__convert(e), last=i == len(node.elts) - 1, end_delim='}') for i, e in
             enumerate(node.elts)] if node.elts else
            [self.__pad_right(j.Empty(random_id(), self.__source_before('}'), Markers.EMPTY), Space.EMPTY)],
            Markers.EMPTY
        )
        return py.CollectionLiteral(
            random_id(),
            prefix,
            Markers.EMPTY,
            py.CollectionLiteral.Kind.SET,
            elements,
            self.__map_type(node)
        )


    def visit_SetComp(self, node):
        return py.ComprehensionExpression(
            random_id(),
            self.__source_before('{'),
            Markers.EMPTY,
            py.ComprehensionExpression.Kind.SET,
            self.__convert(node.elt),
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
        upper = self.__pad_right(
            self.__convert(node.upper) if node.upper else j.Empty(random_id(), Space.EMPTY, Markers.EMPTY),
            self.__source_before(':') if node.step else self.__whitespace('\n'))
        step = self.__pad_right(self.__convert(node.step), self.__whitespace('\n')) if node.step else None
        return py.Slice(
            random_id(),
            prefix,
            Markers.EMPTY,
            lower,
            upper,
            step
        )


    def visit_Starred(self, node):
        return py.Star(
            random_id(),
            self.__source_before('*'),
            Markers.EMPTY,
            py.Star.Kind.LIST,
            self.__convert(node.value),
            self.__map_type(node),
        )


    def visit_Subscript(self, node):
        if isinstance(node.slice, (ast.Constant, ast.Slice)):
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
        else:
            slices = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
            return j.ParameterizedType(
                random_id(),
                self.__whitespace(),
                Markers.EMPTY,
                self.__convert(node.value),
                JContainer(
                    self.__source_before('['),
                    [self.__pad_list_element(self.__convert(s), last=i == len(slices) - 1, end_delim=']') for i, s in enumerate(slices)],
                    Markers.EMPTY
                ),
                None,
                None
            )


    def visit_Tuple(self, node):
        prefix = self.__whitespace()

        omit_parens = True
        if self._source[self._cursor] == '(':
            self._cursor += 1
            omit_parens = False

        elements = JContainer(
            Space.EMPTY,
            [self.__pad_list_element(self.__convert(e), last=i == len(node.elts) - 1,
                                     end_delim=None if omit_parens else ')') for i, e in
             enumerate(node.elts)] if node.elts else
            [self.__pad_right(j.Empty(random_id(), self.__whitespace() if omit_parens else self.__source_before(')'),
                                      Markers.EMPTY), Space.EMPTY)],
            Markers(random_id(), [OmitParentheses(random_id())]) if omit_parens else Markers.EMPTY
        )
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
            if isinstance(node, ast.expr) and not isinstance(node, (ast.Tuple, ast.GeneratorExp)):
                save_cursor = self._cursor

                # noinspection PyUnusedLocal
                # it is used in the lambda below
                prefix = self.__whitespace()

                if self._cursor < len(self._source) and self._source[self._cursor] == '(':
                    self._cursor += 1
                    expr_prefix = self.__whitespace()
                    self._parentheses_stack.append((lambda e, r: j.Parentheses(
                        random_id(),
                        prefix,
                        Markers.EMPTY,
                        self.__pad_right(e.with_prefix(expr_prefix), r)
                    ), self._cursor))
                    # handle nested parens
                    result = self.__convert(node)
                else:
                    self._cursor = save_cursor
                    result = self.visit(cast(ast.AST, node))

                save_cursor_2 = self._cursor
                suffix = self.__whitespace()
                if (len(self._parentheses_stack) > 0 and
                        self._cursor < len(self._source) and
                        self._source[self._cursor] == ')' and
                        (self._parentheses_stack[-1][1] == save_cursor or self._source[self._parentheses_stack[-1][1]:save_cursor].isspace())):
                    self._cursor += 1
                    result = self._parentheses_stack.pop()[0](result, suffix)
                else:
                    self._cursor = save_cursor_2
                return result
            else:
                return self.visit(cast(ast.AST, node))
        else:
            return None


    def __convert_name(self, name: str, name_type: Optional[JavaType] = None) -> NameTree:
        def ident_or_field(parts: List[str]) -> NameTree:
            if len(parts) == 1:
                return j.Identifier(random_id(), self.__source_before(parts[-1]), Markers.EMPTY, [], parts[-1],
                                    name_type, None)
            else:
                return j.FieldAccess(
                    random_id(),
                    self.__whitespace(),
                    Markers.EMPTY,
                    ident_or_field(parts[:-1]),
                    self.__pad_left(
                        self.__source_before('.'),
                        j.Identifier(random_id(), self.__source_before(parts[-1]), Markers.EMPTY, [], parts[-1],
                                     name_type,
                                     None),
                    ),
                    name_type
                )

        return ident_or_field(name.split('.'))


    def __next_lexer_token(self):
        tokens = tokenize(BytesIO(self._source[self._cursor:].encode('utf-8')).readline)
        next(tokens)  # skip ENCODING token
        tok = next(tokens)
        value_source = tok.string
        self._cursor += len(value_source)
        return value_source


    def __convert_all(self, trees: Sequence) -> List[J2]:
        return [self.__convert(tree) for tree in trees]


    def __convert_block(self, statements: Sequence, prefix: str = ':') -> j.Block:
        prefix = self.__source_before(prefix)
        if statements:
            statements = [self.__pad_statement(cast(ast.stmt, s)) for s in statements]
        else:
            statements = [self.__pad_right(j.Empty(random_id(), Space.EMPTY, Markers.EMPTY), Space.EMPTY)]
        return j.Block(
            random_id(),
            prefix,
            Markers.EMPTY,
            JRightPadded(False, Space.EMPTY, Markers.EMPTY),
            statements,
            Space.EMPTY
        )


    def __pad_statement(self, stmt: ast.stmt) -> JRightPadded[Statement]:
        statement = self.__convert(stmt)
        # use whitespace until end of line as padding; what follows will be the prefix of next element
        padding = self.__whitespace('\n')
        if self._cursor < len(self._source) and self._source[self._cursor] == ';':
            self._cursor += 1
            markers = Markers.EMPTY.with_markers([Semicolon(random_id())])
        else:
            markers = Markers.EMPTY
        return JRightPadded(statement, padding, markers)


    def __pad_list_element(self, element: J, last: bool = False, pad_last: bool = True, end_delim: str = None) -> JRightPadded[J]:
        padding = self.__whitespace() if pad_last or not last else Space.EMPTY
        markers = Markers.EMPTY
        if last and self._cursor < len(self._source):
            if self._source[self._cursor] == ',' and end_delim != ',':
                self._cursor += 1
                markers = markers.with_markers([TrailingComma(random_id(), self.__whitespace())])
            if end_delim is not None and self._source[self._cursor] == end_delim:
                self._cursor += 1
        elif not last:
            self._cursor += 1
            markers = Markers.EMPTY
        return JRightPadded(element, padding, markers)


    def __pad_right(self, tree, space: Space) -> JRightPadded[J2]:
        return JRightPadded(tree, space, Markers.EMPTY)


    def __pad_left(self, space: Space, tree) -> JLeftPadded[J2]:
        if isinstance(tree, ast.AST):
            raise ArgumentError(tree, "must be a Tree but is a {}".format(type(tree)))
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


    def __skip(self, tok: Optional[str]) -> Optional[str]:
        if tok is None:
            return None
        if self._source.startswith(tok, self._cursor):
            self._cursor += len(tok)
        return tok


    def __whitespace(self, stop: str = None) -> Space:
        space, self._cursor = self.__format(self._source, self._cursor, stop)
        return space


    def __format(self, source: str, offset: int, stop: str = None) -> Tuple[Space, int]:
        prefix = None
        whitespace = []
        comments = []
        source_len = len(source)
        while offset < source_len:
            char = source[offset]
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
                offset += 1
                while offset < source_len and source[offset] != '\n':
                    comment.append(source[offset])
                    offset += 1
                comments.append(PyComment(''.join(comment), '\n' if offset < source_len else '',
                                          False, Markers.EMPTY))
            else:
                break
            if offset < source_len:
                offset += 1

        if not comments:
            prefix = ''.join(whitespace)
        elif whitespace:
            comments[-1] = comments[-1].with_suffix('\n' + ''.join(whitespace))
        return Space(comments, prefix), offset


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


    # noinspection PyUnusedLocal
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


    def __map_fstring(self, node: ast.JoinedStr, prefix: Space, tok: TokenInfo, tokens: peekable) -> Tuple[
        J, TokenInfo]:
        if tok.type != token.FSTRING_START:
            if len(node.values) == 1 and isinstance(node.values[0], ast.Constant):
                # format specifiers are stored as f-strings in the AST; e.g. `f'{1:n}'`
                format = cast(ast.Constant, node.values[0]).value
                self._cursor += len(format)
                return (j.Literal(
                    random_id(),
                    self.__whitespace(),
                    Markers.EMPTY,
                    format,
                    format,
                    None,
                    self.__map_type(node.values[0]),
                ), next(tokens))
            else:
                delimiter = ''
            consume_end_delim = False
        else:
            delimiter = tok.string
            self._cursor += len(delimiter)
            tok = next(tokens)
            consume_end_delim = True

        # tokenizer tokens: FSTRING_START, FSTRING_MIDDLE, OP, ..., OP, FSTRING_MIDDLE, FSTRING_END
        parts = []
        for value in node.values:
            if tok.type == token.OP and tok.string == '{':
                if not isinstance(value, ast.FormattedValue):
                    # this is the case when using the `=` "debug specifier"
                    continue
                self._cursor += len(tok.string)
                tok = next(tokens)
                if isinstance(cast(ast.FormattedValue, value).value, ast.JoinedStr):
                    nested, tok = self.__map_fstring(cast(ast.JoinedStr, cast(ast.FormattedValue, value).value),
                                                     Space.EMPTY, tok, tokens)
                    expr = self.__pad_right(
                        nested,
                        Space.EMPTY
                    )
                else:
                    expr = self.__pad_right(
                        self.__convert(cast(ast.FormattedValue, value).value),
                        self.__whitespace()
                    )
                    try:
                        while (tokens.peek()).type not in (token.FSTRING_END, token.FSTRING_MIDDLE):
                            tok = next(tokens)
                            if tok.type == token.OP and tok.string == '!':
                                break
                            if tok.type == token.OP and tok.string == '=' and tokens.peek().string in ('!', ':', '}'):
                                break
                    except StopIteration:
                        pass

                # debug specifier
                if tok.type == token.OP and tok.string == '=':
                    self._cursor += len(tok.string)
                    tok = next(tokens)
                    debug = self.__pad_right(True, self.__whitespace('\n'))
                else:
                    debug = None

                # conversion specifier
                if tok.type == token.OP and tok.string == '!':
                    self._cursor += len(tok.string)
                    tok = next(tokens)
                    conv = py.FormattedString.Value.Conversion.ASCII if tok.string == 'a' else py.FormattedString.Value.Conversion.STR if tok.string == 's' else py.FormattedString.Value.Conversion.REPR
                    self._cursor += len(tok.string)
                    tok = next(tokens)
                else:
                    conv = None

                # format specifier
                if tok.type == token.OP and tok.string == ':':
                    self._cursor += len(tok.string)
                    format_spec, tok = self.__map_fstring(
                        cast(ast.JoinedStr, cast(ast.FormattedValue, value).format_spec), Space.EMPTY, next(tokens),
                        tokens)
                else:
                    format_spec = None
                parts.append(py.FormattedString.Value(
                    random_id(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    expr,
                    debug,
                    conv,
                    format_spec
                ))
                self._cursor += len(tok.string)
                tok = next(tokens)
            else:  # FSTRING_MIDDLE
                save_cursor = self._cursor
                while True:
                    self._cursor += len(tok.string) + (1 if tok.string.endswith('{') or tok.string.endswith('}') else 0)
                    if (tok := next(tokens)).type != token.FSTRING_MIDDLE:
                        break
                parts.append(j.Literal(
                    random_id(),
                    Space.EMPTY,
                    Markers.EMPTY,
                    cast(ast.Constant, value).s,
                    self._source[save_cursor:self._cursor],
                    None,
                    self.__map_type(value),
                ))

        if consume_end_delim:
            self._cursor += len(tok.string)  # FSTRING_END token
            tok = next(tokens)
        elif tok.type == token.FSTRING_MIDDLE and len(tok.string) == 0:
            tok = next(tokens)

        return (py.FormattedString(
            random_id(),
            prefix,
            Markers.EMPTY,
            delimiter,
            parts
        ), tok)
