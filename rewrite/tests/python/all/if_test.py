import pytest

from rewrite.test import rewrite_run, python


def test_if():
    # language=python
    rewrite_run(
        python(
            """\
            if True:
                pass
            """
        )
    )


def test_else_single():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(b):
                if b:
                    pass
                else:
                    pass
            """
        )
    )


def test_else_multiple():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(b):
                if b:
                    pass
                else:
                    x = 0
                    pass
            """
        )
    )


def test_elfif_else():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(b):
                if b == 0:
                    pass
                elif b == 1:
                    pass
                else:
                    pass
            """
        )
    )
