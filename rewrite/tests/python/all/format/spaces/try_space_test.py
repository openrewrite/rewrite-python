from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_except():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            try:
                pass
            except  OSError as e:
                pass
            """,
            """\
            try:
                pass
            except OSError as e:
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_multi_except():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            try:
                pass
            except(OSError, IOError) as e:
                pass
            """,
            """\
            try:
                pass
            except (OSError, IOError) as e:
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
