from rewrite.test import rewrite_run, python


def test_del():
    # language=python
    rewrite_run(python("del a"))
