from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, cast

from . import CompilationUnit, ExpressionStatement
from .parser import PythonParserBuilder
from ..java import J, JavaCoordinates, Space
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
        return self._template_parser.parse_expression(scope, self.substitute(parameters), coordinates.loc)

    def substitute(self, *parameters) -> str:
        # FIXME implement
        return self.code


@dataclass
class PythonTemplateParser:
    context_sensitive: bool
    parser_builder: ParserBuilder
    on_after_variable_substitution: Optional[Callable[[str], None]] = None

    def parse_expression(self, scope: Cursor, template: str, loc: Space.Location) -> J:
        cu: CompilationUnit = next(iter(self.parser_builder.build().parse_strings(template)))
        j = cast(ExpressionStatement, cu.statements[0]).expression if isinstance(cu.statements[0], ExpressionStatement) else cu.statements[0]
        return j.with_prefix(cast(J, scope.value).prefix)
