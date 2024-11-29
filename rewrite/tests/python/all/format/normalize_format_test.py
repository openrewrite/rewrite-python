from rewrite.python import NormalizeFormatVisitor, PythonVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


class RemoveDecorators(PythonVisitor):
    def visit_method_declaration(self, method, p):
        return method.with_leading_annotations([])


def test_remove_decorator():
    rewrite_run(
        # language=python
        python(
            """
            from functools import lru_cache

            @lru_cache
            def f(n):
                return n
            """,
            """
            from functools import lru_cache


            def f(n):
                return n
            """
        ),
        spec=RecipeSpec()
        .with_recipes(
            from_visitor(RemoveDecorators()),
            from_visitor(NormalizeFormatVisitor())
        )
    )
