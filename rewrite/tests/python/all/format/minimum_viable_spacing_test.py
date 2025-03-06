from rewrite.java import Block, P, J, MethodInvocation, Space
from rewrite.python import MinimumViableSpacingVisitor, PythonVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_semicolon():
    rewrite_run(
        # language=python
        python(
            """
            def foo():
                print('a'); print('b')
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(MinimumViableSpacingVisitor()))
    )


def test_statement_without_prefix():
    rewrite_run(
        # language=python
        python(
            """
            def foo():
                print('a')
            """,
            """
            def foo():
                print('a')
            print('a')
            """
        ),
        spec=RecipeSpec()
        .with_recipes(
            from_visitor(DuplicateMethod()),
            from_visitor(MinimumViableSpacingVisitor())
        )
    )


def test_statement_with_semicolon():
    rewrite_run(
        # language=python
        python(
            """
            def foo():
                print('a');
            """,
            """
            def foo():
                print('a');print('a');
            """
        ),
        spec=RecipeSpec()
        .with_recipes(
            from_visitor(DuplicateMethod()),
            from_visitor(MinimumViableSpacingVisitor())
        )
    )


class DuplicateMethod(PythonVisitor):
    def visit_block(self, block: Block, p: P) -> J:
        if block.statements and isinstance(block.statements[0], MethodInvocation):
            new_statements = list(block.statements)
            new_statements.append(new_statements[0].with_prefix(Space.EMPTY))
            return block.with_statements(new_statements)
