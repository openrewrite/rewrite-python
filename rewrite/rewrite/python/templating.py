from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from .parser import PythonParserBuilder
from ..parser import ParserBuilder
from ..visitor import Cursor


@dataclass
class PythonTemplate:
    code: str
    on_after_variable_substitution: Optional[Callable[[str], None]] = None
    _template_parser: PythonTemplateParser = field(init=False, repr=False)

    def __init__(self, code: str, parser_builder: PythonParserBuilder,
                 on_after_variable_substitution: Optional[Callable[[str], None]] = None):
        self.code = code
        self.on_after_variable_substitution = on_after_variable_substitution
        self._template_parser = PythonTemplateParser(False, parser_builder, self.on_after_variable_substitution)

    def apply(self, scope: Cursor):
        pass


@dataclass
class PythonTemplateParser:
    context_sensitive: bool
    parser_builder: ParserBuilder
    on_after_variable_substitution: Optional[Callable[[str], None]] = None
