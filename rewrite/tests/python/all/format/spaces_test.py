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


def test_spaces_before_method_call_parentheses():
    style = IntelliJ.spaces()
    style = style.with_before_parentheses(
        style.before_parentheses.with_method_call(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            class Foo:
                def bar (self, a):
                    print (a)
            Foo().bar (1)
            Foo().bar   (1)
            """,
            """
            class Foo:
                def bar(self, a):
                    print(a)
            Foo().bar(1)
            Foo().bar(1)
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


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
