from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_spaces_within_array_access_brackets():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(False)
    ).with_before_parentheses(
        style.before_parentheses.with_method_declaration(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            a [0]
            a  [0 ]
            a[ 0 ]
            a[ 0][ 1]
            a [0 ][1 ]
            a[ 0 ][ 1 ]
            """,
            """
            a[0]
            a[0]
            a[0]
            a[0][1]
            a[0][1]
            a[0][1]
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
