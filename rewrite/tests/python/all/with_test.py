import pytest

from rewrite.test import rewrite_run, python


def test_with():
    # language=python
    rewrite_run(
        python(
            """\
            with len([]) as x:
                pass
            """
        )
    )


def test_with_parens():
    # language=python
    rewrite_run(
        python(
            """\
            with (open('/dev/null') as x):
                pass
            """
        )
    )


def test_async_with():
    # language=python
    rewrite_run(
        python(
            """\
            async with open('/dev/null') as x:
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
