import pytest

from rewrite.test import rewrite_run, python


# noinspection PyCompatibility
@pytest.mark.xfail(reason="Exception groups are not yet supported", strict=True)
def test_with_parentheses():
    # language=python
    rewrite_run(
        python(
            """\
            try:
                foo()
            except* Exception:
                pass
            """
        )
    )
