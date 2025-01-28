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


def test_spaces_after_comma_within_method_declaration_positional_args():
    style = IntelliJ.spaces()

    rewrite_run(
        # language=python
        python(
            """
            def a(a,b):
                pass
            def b(a,  b):
                pass
            def c(a   , b):
                pass
            def d(   a, b, c,d,      e, f):
                pass
            """,
            """
            def a(a, b):
                pass
            def b(a, b):
                pass
            def c(a, b):
                pass
            def d(a, b, c, d, e, f):
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_method_declaration_positional_colon():
    style = IntelliJ.spaces()

    rewrite_run(
        # language=python
        python(
            """
            def a(a,b)   : # cool
                pass
            """,
            """
            def a(a, b): # cool
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_after_comma_within_method_declaration_keyword_arg():
    style = IntelliJ.spaces()

    rewrite_run(
        # language=python
        python(
            """
            def a(a=1,b=2):
                pass
            def b( a=1, b=2   ):
                pass
            def c(       a=1     ,   b=2       ):
                pass
            def d(a=1,b=2,     c=3,    d=4, e=5, f=6):
                pass
            """,
            """
            def a(a=1, b=2):
                pass
            def b(a=1, b=2):
                pass
            def c(a=1, b=2):
                pass
            def d(a=1, b=2, c=3, d=4, e=5, f=6):
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_after_within_method_declaration_type_hints():
    style = IntelliJ.spaces()

    rewrite_run(
        # language=python
        python(
            """
            def x(a :   int   , b = "foo", c : int=2):
                pass
            def y(a :int   , b = "foo", c : int=2):
                pass
            """,
            """
            def x(a: int, b="foo", c: int = 2):
                pass
            def y(a: int, b="foo", c: int = 2):
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_after_within_method_declaration_return_type():
    style = IntelliJ.spaces()

    rewrite_run(
        # language=python
        python(
            """
            def x() -> int:
                pass
            def y(a :   int   , b : int = 2) -> int:
                pass
            """,
            """
            def x() -> int:
                pass
            def y(a: int, b: int = 2) -> int:
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
