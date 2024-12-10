from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_before_colon_class_declaration():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            class A :
                pass
            """,
            """
            class A:
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_before_parentheses_class_declaration():
    style = IntelliJ.spaces()
    style = style.with_before_parentheses(
        style.before_parentheses.with_method_call(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            class A () :
                pass
            """,
            """
            class A():
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_before_parentheses_class_declaration_with_inheritance():
    style = IntelliJ.spaces()
    style = style.with_before_parentheses(
        style.before_parentheses.with_method_call(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            class A (list) :
                pass
            """,
            """
            class A(list):
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_before_parentheses_class_declaration_with_multiple_inheritance():
    style = IntelliJ.spaces()
    style = style.with_before_parentheses(
        style.before_parentheses.with_method_call(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            class Bar:
                pass
            class Foo   (Bar, list) :
                pass
            """,
            """
            class Bar:
                pass
            class Foo(Bar, list):
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_within_parentheses_class_declaration_with_multiple_inheritance():
    style = IntelliJ.spaces()
    style = style.with_before_parentheses(
        style.before_parentheses.with_method_call(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            class Bar:
                pass
            class Foo(Bar,  list) :
                pass
            """,
            """
            class Bar:
                pass
            class Foo(Bar, list):
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
