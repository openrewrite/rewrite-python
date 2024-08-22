from rewrite.test import rewrite_run, python


def test_empty():
    # language=python
    rewrite_run(python("a = f'-{None}-'"))
