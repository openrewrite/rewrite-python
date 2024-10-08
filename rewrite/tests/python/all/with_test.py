import pytest

from rewrite.test import rewrite_run, python


def test_with():
    # language=python
    rewrite_run(
        python(
            """\
            def test(i):
                with len([]) as x:
                    pass
            """
        )
    )


def test_with_no_target():
    # language=python
    rewrite_run(
        python(
            """\
            def test(i):
                with len([]):
                    pass
            """
        )
    )
