import ast
from pathlib import Path
from typing import Iterable, Optional

from rewrite import Parser, ParserInput, ExecutionContext, SourceFile, ParseError
from rewrite.python.__parser_visitor__ import ParserVisitor


class PythonParser(Parser):
    def parse_inputs(self, sources: Iterable[ParserInput], relative_to: Optional[Path],
                     ctx: ExecutionContext) -> Iterable[SourceFile]:
        accepted = (source for source in sources if self.accept(source.path))
        for source in accepted:
            source_str = source.source().read()
            try:
                tree = ast.parse(source_str, source.path)
                cu = ParserVisitor(source_str).visit(tree)
                cu = self.require_print_equals_input(cu, source, relative_to, ctx)
            except Exception as e:
                cu = ParseError.build(self, source, relative_to, ctx, e, None)
            yield cu

    def accept(self, path: Path) -> bool:
        return path.suffix == '.py'

    def source_path_from_source_text(self, prefix: Path, source_code: str) -> Path:
        return prefix / 'source.py'
