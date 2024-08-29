import pytest

from rewrite.test import rewrite_run, python


def test_whitespace_before_colon():
    # language=python
    rewrite_run(
        python(
            """\
            def foo() :
                pass
            """
        )
    )
