from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, cast, List

from . import CompilationUnit, ExpressionStatement, PythonVisitor
from .parser import PythonParserBuilder
from ..java import J, JavaCoordinates, Space, Identifier, P
from ..parser import ParserBuilder
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
        parsed = self._template_parser.parse_expression(scope, substituted, coordinates.loc)
        return substitutions.unsubstitute(parsed)

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


@dataclass
class Substitutions:
    code: str
    parameters: List[Any]

    def substitute(self) -> str:
        result = self.code
        for i, _ in enumerate(self.parameters):
            result = result.replace('#{}', f'__p{i}__')
        return result

    def unsubstitute(self, parsed: J) -> J:
        return cast(J, UnsubstitutionVisitor(self.parameters).visit(parsed, 0))


@dataclass
class UnsubstitutionVisitor(PythonVisitor[int]):
    parameters: List[Any]

    def visit_identifier(self, identifier: Identifier, p: P) -> J:
        if match := re.fullmatch('__p(\d+)__', identifier.simple_name):
            return cast(J, self.parameters[int(match.group(1))])
        return identifier
