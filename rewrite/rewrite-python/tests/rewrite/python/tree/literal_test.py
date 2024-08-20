import ast
import textwrap

from rewrite.python.__parser_visitor__ import ParserVisitor


def test_none(rewrite_remote):
    # language=python
    source = textwrap.dedent("""\
        assert None
        """)

    tree = ast.parse(source)
    visitor = ParserVisitor(source)
    cu = visitor.visit(tree)
    assert cu.print_all() == source


def test_boolean(rewrite_remote):
    # language=python
    source = textwrap.dedent("""\
        assert True or False
        """)

    tree = ast.parse(source)
    visitor = ParserVisitor(source)
    cu = visitor.visit(tree)
    assert cu.print_all() == source


# noinspection PyUnreachableCode
def test_number(rewrite_remote):
    # language=python
    source = textwrap.dedent("""\
        assert 0 or 0.0
        """)

    tree = ast.parse(source)
    visitor = ParserVisitor(source)
    cu = visitor.visit(tree)
    assert cu.print_all() == source
