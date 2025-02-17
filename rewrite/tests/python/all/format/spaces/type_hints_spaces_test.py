from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_type_hint():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            a : int = 1
            a    :    int = 1
            a: int = 1
            a   :int = 1
            """,
            """
            a: int = 1
            a: int = 1
            a: int = 1
            a: int = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_type_hint_union():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            from typing import Union
            a : Union[int,    None] = 1
            a : Union[   int,    None   ] = 1
            a : Union[   int,    float, str ,None  ] = 1
            """,
            """
            from typing import Union
            a: Union[int, None] = 1
            a: Union[int, None] = 1
            a: Union[int, float, str, None] = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_type_hint_union_with_no_space_in_brackets():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            from typing import Union
            a : Union[int,    None] = 1
            a : Union[   int,    None   ] = 1
            a : Union[   int,    float, str ,None  ] = 1
            """,
            """
            from typing import Union
            a: Union[int, None] = 1
            a: Union[int, None] = 1
            a: Union[int, float, str, None] = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

def test_type_hint_union_with_space_in_brackets():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(True)
    )
    rewrite_run(
        # language=python
        python(
            """
            from typing import Union
            a : Union[int,    None] = 1
            a : Union[   int,    None   ] = 1
            a : Union[   int,    float, str ,None  ] = 1
            """,
            """
            from typing import Union
            a: Union[ int, None ] = 1
            a: Union[ int, None ] = 1
            a: Union[ int, float, str, None ] = 1
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )
