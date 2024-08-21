import pytest

from rewrite.test import rewrite_run, python


def test_single():
    # language=python
    rewrite_run(python("assert (True)"))


def test_double():
    # language=python
    rewrite_run(python("assert ((True))"))


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_nested_1():
    # language=python
    rewrite_run(python("assert ((True) or False)"))


def test_nested_2():
    # language=python
    rewrite_run(python("assert (True or (False))"))
