import pytest

from rewrite.test import rewrite_run, python


def test_for():
    # language=python
    rewrite_run(
        python(
            """\
            for x in [1]:
                pass
            """
        )
    )


def test_for_with_destruct():
    # language=python
    rewrite_run(
        python(
            """\
            for x, y in [(1,2),(3,4)]:
                pass
            """
        )
    )


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_for_with_else():
    # language=python
    rewrite_run(
        python(
            """\
            for x in [1]:
                pass
            else:
                pass
            """
        )
    )
