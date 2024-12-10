from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_spaces_within_set_declaration_with_braces_without_space():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_braces(False)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a = { 1, 2, 3 }
            a = {1,2,3}
            a = { 1,2,3}
            a = {1,        2,3}
            a = {1,2, 3}
            a =     {1, 2, 3      }
            """,
            """\
            a = {1, 2, 3}
            a = {1, 2, 3}
            a = {1, 2, 3}
            a = {1, 2, 3}
            a = {1, 2, 3}
            a = {1, 2, 3}
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_set_declaration_with_braces_with_space():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_braces(True)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a = { 1, 2, 3 }
            a = {1,2,3}
            a = { 1,2,3}
            a = {1,        2,3}
            a = {1,2, 3}
            a =     {1, 2, 3      }
            """,
            """\
            a = { 1, 2, 3 }
            a = { 1, 2, 3 }
            a = { 1, 2, 3 }
            a = { 1, 2, 3 }
            a = { 1, 2, 3 }
            a = { 1, 2, 3 }
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_set_declaration_with_braces_with_space_and_trailing_comma():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_braces(True)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a =     {1, 2, 3   ,   }
            """,
            """\
            a = { 1, 2, 3, }
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_set_declaration_with_braces_without_space_and_trailing_comma():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_braces(False)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a =     {1, 2, 3   ,   }
            """,
            """\
            a = {1, 2, 3, }
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
