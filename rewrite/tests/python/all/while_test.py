import pytest

from rewrite.test import rewrite_run, python


def test_while():
    # language=python
    rewrite_run(
        python(
            """\
            def test(i):
                while i < 6:
                    i += 1
            """
        )
    )
