from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_type_hint():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            a : int = 1
            a    :    int = 1
            a: int = 1
            a   :int = 1
            """,
            """
            a: int = 1
            a: int = 1
            a: int = 1
            a: int = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
