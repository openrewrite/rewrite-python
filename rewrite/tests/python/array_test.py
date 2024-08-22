from rewrite.test import rewrite_run, python


def test_empty():
    # language=python
    rewrite_run(python("a = []"))


def test_trailing_comma():
    # language=python
    rewrite_run(python("a = [1, 2,  ]"))
