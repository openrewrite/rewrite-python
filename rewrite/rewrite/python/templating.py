from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, cast, List

from . import CompilationUnit, ExpressionStatement, PythonVisitor
from .parser import PythonParserBuilder
from .printer import PythonPrinter
from .. import PrintOutputCapture
from ..java import J, JavaCoordinates, Space, Identifier, P, Literal
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
        return substitutions.unsubstitute(parsed).with_prefix(cast(J, scope.value).prefix)

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


@dataclass
class UnsubstitutionVisitor(PythonVisitor[int]):
    parameters: List[Any]
    _param_pattern = re.compile('__p(\d+)__')

    def visit_identifier(self, identifier: Identifier, p: P) -> J:
        if match := self._param_pattern.fullmatch(identifier.simple_name):
            return cast(J, self.parameters[int(match.group(1))]).with_prefix(identifier.prefix)
        return identifier
