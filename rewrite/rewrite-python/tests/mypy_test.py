import ast
import textwrap

from rewrite.python.parser.ast_visitor import SimpleASTVisitor


def run_visitor():
    source = textwrap.dedent("""
    def foo():
        print('hello')

    def bar(x):
        return x * 2
    """)

    # Parse the source code into an AST
    tree = ast.parse(source)

    # Create the visitor and visit the AST
    visitor = SimpleASTVisitor()
    visitor.visit(tree)
