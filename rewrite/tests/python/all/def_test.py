import pytest

from rewrite.test import rewrite_run, python


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
