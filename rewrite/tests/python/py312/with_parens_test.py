import pytest

from rewrite.test import rewrite_run, python


# noinspection PyCompatibility
def test_with_parentheses():
    # language=python
    rewrite_run(
        python(
            """\
            with (open('/dev/null') as x):
                pass
            """
        )
    )
