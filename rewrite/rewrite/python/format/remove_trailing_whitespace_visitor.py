from typing import Optional, cast, Union

import rewrite.java as j
import rewrite.python as p
from rewrite.java import Space, J
from rewrite.python import PythonVisitor, CompilationUnit, PySpace
from rewrite.visitor import P


class RemoveTrailingWhitespaceVisitor(PythonVisitor):
    def __init__(self, stop_after: Optional[p.Tree] = None):
        self._stop_after = stop_after

    def visit_compilation_unit(self, compilation_unit: CompilationUnit, p: P) -> J:
        if not compilation_unit.prefix.comments:
            compilation_unit = compilation_unit.with_prefix(Space.EMPTY)
        cu: j.CompilationUnit = cast(j.CompilationUnit, super().visit_compilation_unit(compilation_unit, p))

        if cu.eof.whitespace:
            clean = "".join([_ for _ in cu.eof.whitespace if _ in ['\n', '\r']])
            cu = cu.with_eof(cu.eof.with_whitespace(clean))

        return cu

    def visit_space(self, space: Optional[Space], loc: Optional[Union[PySpace.Location, Space.Location]],
                    p: P) -> Space:
        s = cast(Space, super().visit_space(space, loc, p))

        if not s or not s.whitespace:
            return s

        last_newline = s.whitespace.rfind('\n')
        if last_newline > 0:
            ws = [c for i, c in enumerate(s.whitespace) if i >= last_newline or c in {',', '\r', '\n'}]
            s = s.with_whitespace(''.join(ws))
        return s
