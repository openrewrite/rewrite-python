from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_if_statement():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            if    1 >   2    :
                pass
            """,
            """
            if 1 > 2:
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_if_statement_multiple_conditions():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            if    1 >   2  and   (2 < 3)  :
                pass
            """,
            """
            if 1 > 2 and (2 < 3):
                pass
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_if_else_statement():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            if   1 > 2  :
                a = 1
            else  :
                a = 2
            """,
            """
            if 1 > 2:
                a = 1
            else:
                a = 2
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_if_elif_else_statement():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            if   1 > 2  :
                print(1)
            elif    1 < 2  :
                print(2)
            else  :
                print(3)
            """,
            """
            if 1 > 2:
                print(1)
            elif 1 < 2:
                print(2)
            else:
                print(3)
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
