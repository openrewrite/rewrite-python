from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_with():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            with len([]) as x:
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
