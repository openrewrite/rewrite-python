import ast
import textwrap

from rewrite.python.__parser_visitor__ import ParserVisitor


def test_formatting(rewrite_remote):
    # language=python
    source = textwrap.dedent("""\
        assert \\
        True \\
        ,\\
        'foo'
        """)

    tree = ast.parse(source)
    visitor = ParserVisitor(source)
    cu = visitor.visit(tree)
    assert cu.print_all() == source


def test_with_message(rewrite_remote):
    # language=python
    source = textwrap.dedent("""\
        assert True, 'foo'
        """)

    tree = ast.parse(source)
    visitor = ParserVisitor(source)
    cu = visitor.visit(tree)
    assert cu.print_all() == source
