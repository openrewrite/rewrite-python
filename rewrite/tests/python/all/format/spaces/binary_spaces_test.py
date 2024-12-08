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
            inst: A = A()
            inst.a =1
                """,
            """
            class A:
                def __init__(self):
                    self.a = 1
            inst: A = A()
            inst.a = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


@pytest.mark.parametrize("binary_op", [
    "+", "-", "*", "/", "%", "<", ">", "<=", ">=", "==", "!=", "&", "|", "^", "<<", ">>"
])
def test_spaces_binary_operators(binary_op):
    style = IntelliJ.spaces()
    rewrite_run(
        python(
            f"""
            1{binary_op}1
            1{binary_op} 1
            1 {binary_op}1
            1 {binary_op} 1
            a{binary_op} b
            """,
            f"""
            1 {binary_op} 1
            1 {binary_op} 1
            1 {binary_op} 1
            1 {binary_op} 1
            a {binary_op} b
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


@pytest.mark.parametrize('python_binary_op', ["in", "is", "is not", "not in", "and", "or"])
@pytest.mark.parametrize('left_space', ['', ' '])
@pytest.mark.parametrize('right_space', ['', ' '])
def test_spaces_python_binary_operators_on_lists(python_binary_op, left_space, right_space):
    style = IntelliJ.spaces()
    rewrite_run(
        python(
            f"""
            [3]{left_space}{python_binary_op}{right_space}[1, 2, 3, 4]
            [3]{left_space}{python_binary_op}{left_space}[a]
            """,
            f"""
            [3] {python_binary_op} [1, 2, 3, 4]
            [3] {python_binary_op} [a]
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


@pytest.mark.parametrize('python_binary_op', ["//", "@", "**", "+"])
@pytest.mark.parametrize('left_space', ['', ' '])
@pytest.mark.parametrize('right_space', ['', ' '])
def test_spaces_python_binary_operators_numbers(python_binary_op, left_space, right_space):
    style = IntelliJ.spaces()
    rewrite_run(
        python(
            f"""
            a{left_space}{python_binary_op}{right_space}b
            """,
            f"""
            a {python_binary_op} b
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


@pytest.mark.parametrize('left_space', ['', ' '])
@pytest.mark.parametrize('right_space', ['', ' '])
def test_spaces_python_binary_operators_string(left_space, right_space):
    style = IntelliJ.spaces()
    rewrite_run(
        python(
            f"""
            "Hello"{left_space}+{right_space}"World!"
            """,
            """
            "Hello" + "World!"
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
