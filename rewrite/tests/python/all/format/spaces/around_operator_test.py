from typing import Callable

from rewrite.python import IntelliJ, SpacesVisitor, SpacesStyle
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def get_around_operator_style(
        _with: Callable[[SpacesStyle.AroundOperators], SpacesStyle.AroundOperators]) -> SpacesStyle:
    style = IntelliJ.spaces()
    return style.with_around_operators(
        _with(style.around_operators)
    )


def test_spaces_around_assignment():
    style = get_around_operator_style(lambda x: x.with_assignment(True))
    rewrite_run(
        # language=python
        python(
            """
            a  =  1
            a=  1
            a  =1
            a=1
            """,
            """
            a = 1
            a = 1
            a = 1
            a = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_assignment(False))
    rewrite_run(
        # language=python
        python(
            """
            a  =  1
            a=  1
            a  =1
            a=1
            """,
            """
            a=1
            a=1
            a=1
            a=1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_equality():
    style = get_around_operator_style(lambda x: x.with_equality(True))
    rewrite_run(
        # language=python
        python(
            """
            a  ==  1
            a==  1
            a  ==1
            a==1
            """,
            """
            a == 1
            a == 1
            a == 1
            a == 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_equality(False))
    rewrite_run(
        # language=python
        python(
            """
            a  ==  1
            a==  1
            a  ==1
            a==1
            """,
            """
            a==1
            a==1
            a==1
            a==1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_relational():
    style = get_around_operator_style(lambda x: x.with_relational(True))
    rewrite_run(
        # language=python
        python(
            """
            a  <  1
            a<  1
            a  <1
            a<1
            """,
            """
            a < 1
            a < 1
            a < 1
            a < 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_relational(False))
    rewrite_run(
        # language=python
        python(
            """
            a  <  1
            a<  1
            a  <1
            a<1
            """,
            """
            a<1
            a<1
            a<1
            a<1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_bitwise():
    style = get_around_operator_style(lambda x: x.with_bitwise(True))
    rewrite_run(
        # language=python
        python(
            """
            a  &  1
            a&  1
            a  &1
            a&1
            """,
            """
            a & 1
            a & 1
            a & 1
            a & 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_bitwise(False))
    rewrite_run(
        # language=python
        python(
            """
            a  &  1
            a&  1
            a  &1
            a&1
            """,
            """
            a&1
            a&1
            a&1
            a&1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_additive():
    style = get_around_operator_style(lambda x: x.with_additive(True))
    rewrite_run(
        # language=python
        python(
            """
            a  +  1
            a+  1
            a  +1
            a+1
            """,
            """
            a + 1
            a + 1
            a + 1
            a + 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_additive(False))
    rewrite_run(
        # language=python
        python(
            """
            a  +  1
            a+  1
            a  +1
            a+1
            """,
            """
            a+1
            a+1
            a+1
            a+1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_multiplicative():
    style = get_around_operator_style(lambda x: x.with_multiplicative(True))
    rewrite_run(
        # language=python
        python(
            """
            a  *  1
            a*  1
            a  *1
            a*1
            """,
            """
            a * 1
            a * 1
            a * 1
            a * 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_multiplicative(False))
    rewrite_run(
        # language=python
        python(
            """
            a  *  1
            a*  1
            a  *1
            a*1
            """,
            """
            a*1
            a*1
            a*1
            a*1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_shift():
    style = get_around_operator_style(lambda x: x.with_shift(True))
    rewrite_run(
        # language=python
        python(
            """
            a  <<  1
            a<<  1
            a  <<1
            a<<1
            """,
            """
            a << 1
            a << 1
            a << 1
            a << 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_shift(False))
    rewrite_run(
        # language=python
        python(
            """
            a  <<  1
            a<<  1
            a  <<1
            a<<1
            """,
            """
            a<<1
            a<<1
            a<<1
            a<<1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_power():
    style = get_around_operator_style(lambda x: x.with_power(True))
    rewrite_run(
        # language=python
        python(
            """
            a  **  1
            a**  1
            a  **1
            a**1
            """,
            """
            a ** 1
            a ** 1
            a ** 1
            a ** 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_power(False))
    rewrite_run(
        # language=python
        python(
            """
            a  **  1
            a**  1
            a  **1
            a**1
            """,
            """
            a**1
            a**1
            a**1
            a**1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_eq_in_named_parameter():
    style = get_around_operator_style(lambda x: x.with_eq_in_named_parameter(True))
    rewrite_run(
        # language=python
        python(
            """
            def func(a  =  1): pass
            def func(a=  1): pass
            def func(a  =1): pass
            def func(a=1): pass
            """,
            """
            def func(a = 1): pass
            def func(a = 1): pass
            def func(a = 1): pass
            def func(a = 1): pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_eq_in_named_parameter(False))
    rewrite_run(
        # language=python
        python(
            """
            def func(a  =  1): pass
            def func(a=  1): pass
            def func(a  =1): pass
            def func(a=1): pass
            """,
            """
            def func(a=1): pass
            def func(a=1): pass
            def func(a=1): pass
            def func(a=1): pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_around_eq_in_keyword_argument():
    style = get_around_operator_style(lambda x: x.with_eq_in_keyword_argument(True))
    rewrite_run(
        # language=python
        python(
            """
            func(a  =  1)
            func(a=  1)
            func(a  =1)
            func(a=1)
            """,
            """
            func(a = 1)
            func(a = 1)
            func(a = 1)
            func(a = 1)
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

    style = get_around_operator_style(lambda x: x.with_eq_in_keyword_argument(False))
    rewrite_run(
        # language=python
        python(
            """
            func(a  =  1)
            func(a=  1)
            func(a  =1)
            func(a=1)
            """,
            """
            func(a=1)
            func(a=1)
            func(a=1)
            func(a=1)
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
