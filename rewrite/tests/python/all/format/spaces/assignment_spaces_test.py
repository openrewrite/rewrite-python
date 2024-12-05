import pytest

from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_spaces_around_assignment():
    style = IntelliJ.spaces()
    style = style.with_around_operators(
        style.around_operators.with_assignment(True)
    )
    rewrite_run(
        # language=python
        python(
            """
            a=1
            a= 1
            a =1
            def foo(x):
                x =1
            """,
            """
            a = 1
            a = 1
            a = 1
            def foo(x):
                x = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_chained_assignment():
    style = IntelliJ.spaces()
    style = style.with_around_operators(
        style.around_operators.with_assignment(True)
    )
    rewrite_run(
        # language=python
        python(
            """
            a =b= 1 +2
            a=b=1 +2
            a=b =1 +2
            """,
            """
            a = b = 1 + 2
            a = b = 1 + 2
            a = b = 1 + 2
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_assignment_op():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            a+=1
            a-= 1
            a +=1
            """,
            """
            a += 1
            a -= 1
            a += 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_member_reference():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            class A:
                def __init__(self):
                    self.a= 1
            inst : A = A()
            inst.a =1
                """,
            """
            class A:
                def __init__(self):
                    self.a = 1
            inst : A = A()
            inst.a = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
