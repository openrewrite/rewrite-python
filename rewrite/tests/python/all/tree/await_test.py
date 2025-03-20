from rewrite.test import rewrite_run, python


def test_await():
    # language=python
    rewrite_run(python("a = await 1"))
