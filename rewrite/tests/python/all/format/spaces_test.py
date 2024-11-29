from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_before_parentheses_method_declaration():
    style = IntelliJ.spaces()
    style = style.with_before_parentheses(
        style.before_parentheses.with_method_declaration(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            class Foo:
                def getter  (self, row):
                    pass
            """,
            """
            class Foo:
                def getter(self, row):
                    pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
