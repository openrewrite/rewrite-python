import unittest
import ast
import textwrap

from rewrite.python.parser.parser_visitor import ParserVisitor


class TestParserVisitor(unittest.TestCase):
    def test_visitor(self):
        # language=Python
        source = textwrap.dedent("""
            def bar(x):
                x = x + 1
                return x
            """)

        # Parse the source code into an AST
        tree = ast.parse(source)

        # Create the visitor and visit the AST
        visitor = ParserVisitor(source)
        visitor.visit(tree)

    def test_assert(self):
        # language=Python
        source = textwrap.dedent("""
            assert True
            """)

        tree = ast.parse(source)
        visitor = ParserVisitor(source)
        cu = visitor.visit(tree)
        assert cu is not None
