from rewrite.test import rewrite_run, python


def test_continue():
    rewrite_run(python("continue"))
