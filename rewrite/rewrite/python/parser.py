import ast
import traceback
from pathlib import Path
from typing import Iterable, Optional

from rewrite import Parser, ParserInput, ExecutionContext, SourceFile, ParseError
from rewrite.parser import require_print_equals_input, ParserBuilder
from ._parser_visitor import ParserVisitor
from .tree import CompilationUnit


class PythonParser(Parser):
    def parse_inputs(self, sources: Iterable[ParserInput], relative_to: Optional[Path],
                     ctx: ExecutionContext) -> Iterable[SourceFile]:
        accepted = (source for source in sources if self.accept(source.path))
        for source in accepted:
            try:
                source_str = source.source().read()
                tree = ast.parse(source_str, source.path)
                cu = ParserVisitor(source_str).visit(tree)
                cu = require_print_equals_input(self, cu, source, relative_to, ctx)
            except Exception as e:
                traceback.print_exc()
                cu = ParseError.build(self, source, relative_to, ctx, e)
            yield cu

    def accept(self, path: Path) -> bool:
        return path.suffix == '.py'

    def source_path_from_source_text(self, prefix: Path, source_code: str) -> Path:
        return prefix / 'source.py'


class PythonParserBuilder(ParserBuilder):
    def __init__(self):
        self._source_file_type = type(CompilationUnit)
        self._dsl_name = 'python'

    def build(self) -> Parser:
        return PythonParser()
