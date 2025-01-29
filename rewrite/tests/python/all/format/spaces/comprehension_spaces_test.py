import pytest

from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


@pytest.mark.parametrize("within_brackets", [False, True])
def test_spaces_with_list_comprehension(within_brackets):
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(within_brackets)
    )
    _s = " " if within_brackets else ""
    rewrite_run(
        # language=python
        python(
            """\
            a =   [  i*2 for   i   in  range(0, 10)]
            a =   [  i*2 for   i   in  [1, 2, 3   ]]
            """,
            f"""\
            a = [i * 2 for i in range(0, 10)]
            a = [i * 2 for i in [1, 2, 3]]
            """.replace("[", "[" + _s).replace("]", _s + "]")
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_with_generator_comprehension():
    style = IntelliJ.spaces()

    rewrite_run(
        # language=python
        python(
            """\
            a =  (  i*2 for   i   in  range(0, 10))
            """,
            f"""\
            a = (i * 2 for i in range(0, 10))
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


@pytest.mark.parametrize("within_brackets", [False, True])
def test_spaces_with_list_comprehension_with_condition(within_brackets):
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(within_brackets)
    )
    _s = " " if within_brackets else ""
    rewrite_run(
        # language=python
        python(
            """\
            a =   [   i*    2 for i   in  range(0, 10)   if   i % 2 ==  0   ]
            """,
            """\
            a = [i * 2 for i in range(0, 10) if i % 2 == 0]
            """.replace("[", "[" + _s).replace("]", _s + "]")
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


@pytest.mark.parametrize("within_braces", [False, True])
def test_spaces_with_set_comprehension(within_braces):
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_braces(within_braces)
    )
    _s = " " if within_braces else ""
    rewrite_run(
        # language=python
        python(
            """\
            a = {i*2 for i   in  range(0, 10)}
            a = {i for i   in  {1, 2, 3   }}
            """,
            """\
            a = {i * 2 for i in range(0, 10)}
            a = {i for i in {1, 2, 3}}
            """.replace("{", "{" + _s).replace("}", _s + "}")
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


@pytest.mark.parametrize("within_braces", [False, True])
def test_spaces_with_dict_comprehension(within_braces):
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_braces(within_braces)
    )
    _s = " " if within_braces else ""
    rewrite_run(
        # language=python
        python(
            """\
            a = {i: i*2 for i   in  range(0, 10)}
            a = {i: i for i   in  [1, 2, 3]}
            a = {k:   v*2 for k,v   in  {   "a": 2, "b": 4}.items( ) }
            """,
            """\
            a = {i: i * 2 for i in range(0, 10)}
            a = {i: i for i in [1, 2, 3]}
            a = {k: v * 2 for k, v in {"a": 2, "b": 4}.items()}
            """.replace("{", "{" + _s).replace("}", _s + "}")
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_with_dict_comprehension():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            a = {k:   1 }
            a = {k:   1 ** 2}
            def dict_comprehension_test(self):
                keys = ['a', 'b', 'c']
                values = [1, 2, 3]
                return {k  :     v ** 2
                        for k, v in zip(keys, values)
                        }
            """,
            """\
            a = {k: 1}
            a = {k: 1 ** 2}
            def dict_comprehension_test(self):
                keys = ['a', 'b', 'c']
                values = [1, 2, 3]
                return {k: v ** 2
                        for k, v in zip(keys, values)
                        }
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
