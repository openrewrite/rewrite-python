from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, cast, List, Type

from . import CompilationUnit, ExpressionStatement, PythonVisitor
from .parser import PythonParserBuilder
from .printer import PythonPrinter
from .. import PrintOutputCapture, Tree
from ..java import J, JavaCoordinates, Space, Identifier, P, Literal, Expression, Statement, Block
from ..parser import ParserBuilder
from ..utils import list_flat_map
from ..visitor import Cursor


@dataclass
class PythonTemplate:
    code: str
    on_after_variable_substitution: Optional[Callable[[str], None]] = None
    _template_parser: PythonTemplateParser = field(init=False, repr=False)

    def __init__(self, code: str, parser_builder: PythonParserBuilder = PythonParserBuilder(),
                 on_after_variable_substitution: Optional[Callable[[str], None]] = None):
        self.code = code
        self.on_after_variable_substitution = on_after_variable_substitution
        self._template_parser = PythonTemplateParser(False, parser_builder, self.on_after_variable_substitution)

    def apply(self, scope: Cursor, coordinates: JavaCoordinates, *parameters) -> J:
        substitutions = self.substitutions(*parameters)
        substituted = substitutions.substitute()
        if self.on_after_variable_substitution:
            self.on_after_variable_substitution(substituted)

        return PythonTemplatePythonExtension(self._template_parser, substitutions, substituted, coordinates)\
            .visit(cast(Tree, scope.value), 0, scope.parent_or_throw)

    def substitutions(self, parameters: List[Any]) -> Substitutions:
        return Substitutions(self.code, parameters)


@dataclass
class PythonTemplateParser:
    context_sensitive: bool
    parser_builder: ParserBuilder
    on_after_variable_substitution: Optional[Callable[[str], None]] = None

    def parse_expression(self, scope: Cursor, template: str, loc: Space.Location) -> J:
        cu: CompilationUnit = next(iter(self.parser_builder.build().parse_strings(template)))
        j = cast(ExpressionStatement, cu.statements[0]).expression if isinstance(cu.statements[0],
                                                                                 ExpressionStatement) else \
            cu.statements[0]
        return j.with_prefix(cast(J, scope.value).prefix)

    def parse_block_statements(self, cursor: Cursor, expected: Type, template: str, loc: Space.Location, mode: JavaCoordinates.Mode) -> List[J]:
        cu: CompilationUnit = next(iter(self.parser_builder.build().parse_strings(template)))
        return cu.statements


@dataclass
class Substitutions:
    code: str
    parameters: List[Any]

    def substitute(self) -> str:
        result = ""
        pos = 0
        param_count = 0
        named_index = {}

        while True:
            # Find next #{
            start = self.code.find('#{', pos)
            if start == -1:
                # No more parameters, add remaining code
                result += self.code[pos:]
                break

            # Add code before the #{
            result += self.code[pos:start]

            # Find matching }
            brace_count = 1
            i = start + 2  # Skip past #{
            while i < len(self.code) and brace_count > 0:
                if self.code[i] == '{':
                    brace_count += 1
                elif self.code[i] == '}':
                    brace_count -= 1
                i += 1

            if brace_count > 0:
                raise ValueError("Unmatched { in template")
            pattern = self.code[start + 2:i - 1].strip()
            param_index = param_count if not pattern or pattern.find('any()') >= 0 else named_index[pattern]
            if (sep := pattern.find(':')) >= 0:
                named_index[pattern[0:sep]] = param_index

            # Replace the #{...} with parameter placeholder
            result += f'__p{param_index}__' if pattern else self.substitute_untyped(param_index)
            if not pattern or pattern.find('any()') >= 0:
                param_count += 1

            pos = i

        return result

    def substitute_untyped(self, index: int) -> str:
        param = self.parameters[index]
        if isinstance(param, Literal):
            capture = PrintOutputCapture(0)
            PythonPrinter().visit(param, capture)
            return capture.get_out()
        return str(param)

    def unsubstitute(self, parsed: J) -> J:
        return cast(J, UnsubstitutionVisitor(self.parameters).visit(parsed, 0))

    def unsubstitute_all(self, parsed: List[J]) -> List[J]:
        return [self.unsubstitute(j) for j in parsed]


@dataclass
class UnsubstitutionVisitor(PythonVisitor[int]):
    parameters: List[Any]
    _param_pattern = re.compile('__p(\d+)__')

    def visit_identifier(self, identifier: Identifier, p: P) -> J:
        if match := self._param_pattern.fullmatch(identifier.simple_name):
            return cast(J, self.parameters[int(match.group(1))]).with_prefix(identifier.prefix)
        return identifier

@dataclass
class PythonTemplatePythonExtension(PythonVisitor[int]):
    template_parser: PythonTemplateParser
    substitutions: Substitutions
    substituted_template: str
    coordinates: JavaCoordinates

    def __post_init__(self):
        self.insertion_point = self.coordinates.tree
        self.loc = self.coordinates.loc
        self.mode = self.coordinates.mode

    def visit_expression(self, expression: Expression, p: int) -> J:
        if (self.loc == Space.Location.EXPRESSION_PREFIX or self.loc == Space.Location.STATEMENT_PREFIX and
            isinstance(expression, Statement)) and expression.is_scope(self.insertion_point):
            parsed = self.template_parser.parse_expression(self.cursor, self.substituted_template, self.loc)
            return self.auto_format(self.substitutions.unsubstitute(parsed).with_prefix(expression.prefix), p)
        return expression

    def visit_block(self, block: Block, p: P) -> J:
        if self.loc == Space.Location.BLOCK_END and block.is_scope(self.insertion_point):
            parsed = self.template_parser.parse_block_statements(Cursor(self.cursor, self.insertion_point), Statement,
                                                                 self.substituted_template, self.loc, self.mode)
            gen: List[Statement] = self.substitutions.unsubstitute_all(parsed)
            return self.auto_format(block.with_statements(block.statements + gen), p, self.cursor.parent) if gen else block
        if self.loc == Space.Location.STATEMENT_PREFIX:
            return self.auto_format(block.with_statements(list_flat_map(lambda s: self.get_replacements(s) if s.is_scope(self.insertion_point) else s, block.statements)), p, self.cursor.parent)
        return super().visit_block(block, p)

    def visit_statement(self, statement: Statement, p: P) -> J:
        return statement
        # if (self.loc == Space.Location.STATEMENT_PREFIX and statement.is_scope(self.insertion_point):
        #     parsed = self.template_parser.parse_expression(self.cursor, self.substituted_template, self.loc)
        #     return self.auto_format(self.substitutions.unsubstitute(parsed).with_prefix(expression.prefix), p)
        # return expression

    def get_replacements(self, statement: Statement) -> List[J]:
        parsed = self.template_parser.parse_block_statements(Cursor(self.cursor, self.insertion_point), Statement, self.substituted_template, self.loc, self.mode)
        gen = self.substitutions.unsubstitute_all(parsed)
        formatted = [s.with_prefix(statement.prefix.with_comments([])) for s in gen]

        if self.mode == JavaCoordinates.Mode.REPLACE:
            return formatted
        elif self.mode == JavaCoordinates.Mode.BEFORE:
            return formatted + [statement]
        else:
            return [statement] + formatted
