from rewrite.python import IntelliJ, SpacesVisitor
from rewrite.test import rewrite_run, python, RecipeSpec, from_visitor


def test_spaces_within_array_declaration_brackets():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(False)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a = [ 1, 2, 3 ]
            a = [1,2,3]
            a = [ 1,2,3]
            a = [1,        2,3]
            a = [1,2, 3]
            a =     [1, 2, 3      ]
            """,
            """\
            a = [1, 2, 3]
            a = [1, 2, 3]
            a = [1, 2, 3]
            a = [1, 2, 3]
            a = [1, 2, 3]
            a = [1, 2, 3]
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_array_declaration_brackets_trailing_comma():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(False)
    )
    rewrite_run(
        # language=python
        python(
            """\
            a =     [1, 2, 3   ,   ]
            """,
            """\
            a = [1, 2, 3, ]
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_array_access_brackets():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(False)
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


def test_spaces_within_array_access_brackets_slice():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            a[:  ] =  a[ : ] = a[  :]
            a[0:   42] = a[0:42]
            a[0 : ] = a[0 :]
            """,
            """
            a[:] = a[:] = a[:]
            a[0:42] = a[0:42]
            a[0:] = a[0:]
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_array_access_brackets_slice_with_steps():
    style = IntelliJ.spaces()
    style = style.with_within(
        style.within.with_brackets(False)
    )
    rewrite_run(
        # language=python
        python(
            """
            a[  0  : 42 : 2] = a[42:0: -2 ]
            a[: : ] = a[:: ] = a[   : : ] = a[: :]
            """,
            """
            a[0:42:2] = a[42:0:-2]
            a[::] = a[::] = a[::] = a[::]
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )


def test_spaces_within_array_access_brackets_slice_with_expressions():
    style = IntelliJ.spaces()
    rewrite_run(
        # language=python
        python(
            """
            a[  (1+1 + 1)  :   41 + 1 : 4] = a[ 0 : 3*3 : b ]
            """,
            """
            a[(1 + 1 + 1):41 + 1:4] = a[0:3 * 3:b]
            """
        ),
        spec=RecipeSpec()
        .with_recipe(from_visitor(SpacesVisitor(style)))
    )

