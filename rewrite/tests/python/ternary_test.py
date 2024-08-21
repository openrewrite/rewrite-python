from rewrite.test import rewrite_run, python


def test_simple():
    # language=python
    rewrite_run(python("assert True if True else False"))
