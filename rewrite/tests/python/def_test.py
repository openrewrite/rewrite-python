import pytest

from rewrite.test import rewrite_run, python


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_async_def():
    # language=python
    rewrite_run(
        python(
            """\
            async def main():
                pass
            """
        )
    )
