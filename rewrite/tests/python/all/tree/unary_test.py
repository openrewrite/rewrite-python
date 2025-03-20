import pytest

from rewrite.test import rewrite_run, python


def test_bool_ops():
    # language=python
    rewrite_run(python("assert not True"))


def test_arithmetic_ops():
    # language=python
    rewrite_run(python("assert +1"))
    # language=python
    rewrite_run(python("assert -1"))
    # language=python
    rewrite_run(python("assert ~1"))
