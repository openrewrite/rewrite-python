from rewrite.test import rewrite_run, python


def test_yield():
    # language=python
    rewrite_run(python("yield 1"))