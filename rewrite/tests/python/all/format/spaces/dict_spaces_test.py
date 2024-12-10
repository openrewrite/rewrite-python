import pytest

from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_spaces_within_dict_declaration():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            a = { "a" :  1    }
            """,
            """\
            a = {"a": 1}
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_dict_declaration_multi_key():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            a = { "a" :  1, "b": 2  ,   "c": 3  }
            """,
            """\
            a = {"a": 1, "b": 2, "c": 3}
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_dict_declaration_nested():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            a = { "a" :  {"x": 1}, "b": {"y": {"z": [{ "a" : 1}    , {"b":  "2"}]}},   "c": 3  }
            """,
            """\
            a = {"a": {"x": 1}, "b": {"y": {"z": [{"a": 1}, {"b": "2"}]}}, "c": 3}
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_dict_declaration_multi_key_trailing_comma():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            a = { "a" :  1, "b": 2  ,   "c": 3,  }
            a = { "a" :  1, "b": 2  ,   "c": 3,}
            """,
            """\
            a = {"a": 1, "b": 2, "c": 3, }
            a = {"a": 1, "b": 2, "c": 3, }
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_dict_declaration_braces_false():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_braces(False)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a = { "a": 1, "b": 2     }
            a = {"a": 1, "b": 2 }
            a = {   "a": 1, "b": 2}
            a = {   "a": 1, "b": 2,}
            """,
            """\
            a = {"a": 1, "b": 2}
            a = {"a": 1, "b": 2}
            a = {"a": 1, "b": 2}
            a = {"a": 1, "b": 2, }
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_dict_declaration_braces_true():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_braces(True)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a = { "a": 1, "b": 2     }
            a = {"a": 1, "b": 2 }
            a = {   "a": 1, "b": 2}
            a = {   "a": 1, "b": 2,}
            """,
            """\
            a = { "a": 1, "b": 2 }
            a = { "a": 1, "b": 2 }
            a = { "a": 1, "b": 2 }
            a = { "a": 1, "b": 2, }
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


@pytest.mark.skip("Not implemented")
def test_spaces_within_dict_declaration_braces_multi_line():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """\
            a = {"a": 1,
            "b": 2}
            """,
            """\
            a = {"a": 1,
                 "b": 2}
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
