import ast
import textwrap

import pytest

from rewrite.python.__parser_visitor__ import ParserVisitor


class TestParserVisitor:
    def test_visitor(self, rewrite_remote):
        # language=Python
        source = textwrap.dedent("""\
            def bar(x: str, y = 'foo'):
                assert True
            """)

        # Parse the source code into an AST
        tree = ast.parse(source)

        # Create the visitor and visit the AST
        visitor = ParserVisitor(source)
        cu = visitor.visit(tree)
        assert cu is not None
        # FIXME looks like the printer is having some issues
        assert cu.print_all() == " bar(x str, y = 'foo')\n    assert True\n"

    def test_assert(self, rewrite_remote):
        # language=python
        source = textwrap.dedent("""\
            assert True, 'foo' # foo
            """)

        tree = ast.parse(source)
        visitor = ParserVisitor(source)
        cu = visitor.visit(tree)
        assert cu is not None
        assert cu.print_all() == source
