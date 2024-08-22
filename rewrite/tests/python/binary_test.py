import pytest

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


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_eq_ops():
    # language=python
    rewrite_run(python("assert 1 == 1"))
    # language=python
    rewrite_run(python("assert 1 != 2"))
    # language=python
    rewrite_run(python("assert 1 is 1"))
    # language=python
    rewrite_run(python("assert 1 is not 2"))


def test_comparison_ops():
    # language=python
    rewrite_run(python("assert 1 < 2"))
    # language=python
    rewrite_run(python("assert 1 <= 2"))
    # language=python
    rewrite_run(python("assert 2 > 1"))
    # language=python
    rewrite_run(python("assert 2 >= 1"))