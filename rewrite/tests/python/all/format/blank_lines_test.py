from rewrite.java import Space
from rewrite.python import IntelliJ
from rewrite.python.format import BlankLinesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_remove_leading_module_blank_lines():
    rewrite_run(
        # language=python
        python(
            """


            print('foo')
            """,
            """print('foo')
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(BlankLinesVisitor(IntelliJ.blank_lines())))
    )
