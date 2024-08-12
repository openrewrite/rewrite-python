import ast
import textwrap

from rewrite.python.parser.parser_visitor import ParserVisitor


def test_visitor():
    source = textwrap.dedent("""
    def bar(x):
        x = x + 1
        return x
    """)

    # Parse the source code into an AST
    tree = ast.parse(source)

    # Create the visitor and visit the AST
    visitor = ParserVisitor()
    visitor.visit(tree)
