import pytest

from rewrite.test import rewrite_run, python


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_global():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
              global x
              x = 1
            """
        )
    )
