from rewrite.test import rewrite_run, python


def test_break():
    rewrite_run(python("continue"))