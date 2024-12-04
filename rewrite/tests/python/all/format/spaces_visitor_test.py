import pytest

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


def test_spaces_within_method_call_parameters_with_args():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(True).with_method_call_parentheses(False)
    ).with_before_parentheses(
        style.before_parentheses.with_method_declaration(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            foo( 1 )
            foo( 1, 2 )
            foo( 1,2,3 )
            """,
            """
            foo(1)
            foo(1, 2)
            foo(1, 2, 3)
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_method_call_parameters_no_args():
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
            foo( )
            """,
            """
            foo()
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
            def x(a : int   , b : int = 2):
                pass
            def y(a :int   , b : int = 2):
                pass
            """,
            """
            def x(a : int, b : int = 2):
                pass
            def y(a : int, b : int = 2):
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_after_comma_method_call():
    style = IntelliJ.spaces()
    style = style.with_other(
        style.other.with_after_comma(True)
    )
    rewrite_run(
        # language=python
        python(
            """
            foo(1 )
            foo(1, 2)
            foo(1,2)
            foo(1, 2,3)
            """,
            """
            foo(1)
            foo(1, 2)
            foo(1, 2)
            foo(1, 2, 3)
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


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


def test_spaces_around_assignment():
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
