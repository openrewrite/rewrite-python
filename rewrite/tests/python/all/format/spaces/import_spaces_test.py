from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_import_import_spaces():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            import    os
            import os, uuid,     os.path
            """,
            """
            import os
            import os, uuid, os.path
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_import_import_spaces_with_alias():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            import    os   as   a
            """,
            """
            import os as a
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_import_multi_import_spaces():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            from os import path   ,    system , environ
            """,
            """
            from os import path, system, environ
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_import_multi_import_spaces_with_alias():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            import    os as a
            import os   ,   uuid  as   b  ,     os.path as c
            """,
            """
            import os as a
            import os, uuid as b, os.path as c
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
