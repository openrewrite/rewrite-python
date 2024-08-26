from rewrite.test import rewrite_run, python


def test_comment():
    # language=python
    rewrite_run(python("assert 1 # type: foo"))
