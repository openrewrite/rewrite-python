from rewrite.test import rewrite_run, python


def test_bool_ops():
    # language=python
    rewrite_run(python("assert True or False"))
    # language=python
    rewrite_run(python("assert True and False"))


def test_arithmetic_ops():
    # language=python
    rewrite_run(python("assert 1 + 2"))
    # language=python
    rewrite_run(python("assert 1 - 2"))
    # language=python
    rewrite_run(python("assert 1 * 2"))
    # language=python
    rewrite_run(python("assert 1 / 2"))
    # language=python
    rewrite_run(python("assert 1 % 2"))
