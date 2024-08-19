import ast
import textwrap

import pytest

from rewrite import Cursor
from rewrite.python.__parser_visitor__ import ParserVisitor


class TestParserVisitor:
    def test_visitor(self):
        # language=Python
        source = textwrap.dedent("""\
            def bar(x):
                x = x + 1
                return x
            """)

        # Parse the source code into an AST
        tree = ast.parse(source)

        # Create the visitor and visit the AST
        visitor = ParserVisitor(source)
        visitor.visit(tree)

    def test_assert(self, rewrite_remote):
        # language=python
        source = textwrap.dedent("""\
            assert True
            """)

        tree = ast.parse(source)
        visitor = ParserVisitor(source)
        cu = visitor.visit(tree)
        assert cu is not None
        print(rewrite_remote.client.print(Cursor(None, cu)))

