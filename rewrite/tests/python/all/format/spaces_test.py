from rewrite import NamedStyles
from rewrite.python import AutoFormat, PythonParserBuilder, IntelliJ
from rewrite.test import rewrite_run, python, RecipeSpec


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
        .with_recipe(AutoFormat())
        .with_parsers([PythonParserBuilder().styles(NamedStyles.build(style))])
    )
