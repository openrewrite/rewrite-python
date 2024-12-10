from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_spaces_within_array_access_brackets():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            for i   in  [1,   2,3] :
                print("Hello")
            """,
            """\
            for i in [1, 2, 3]:
                print("Hello")
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
