from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_spaces_nested_parenthesis():
    style = IntelliJ.spaces()
    style = style.with_around_operators(
        style.around_operators.with_assignment(True)
    )
    rewrite_run(
        # language=python
        python(
            """\
            ((  (   (1 + 2   ) )  )  )
            """,
            """\
            ((((1 + 2))))
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_nested_parenthesis_and_assignment():
    style = IntelliJ.spaces()
    style = style.with_around_operators(
        style.around_operators.with_assignment(True)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a =   ((  (   (1 + 2   ) )  )  )
            b =   ((  (   (1 + 2   ) )  )  ) + ((  (   (1 + 2   ) )  )  )
            """,
            """\
            a = ((((1 + 2))))
            b = ((((1 + 2)))) + ((((1 + 2))))
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
