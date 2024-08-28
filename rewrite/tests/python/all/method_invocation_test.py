import pytest

from rewrite.test import rewrite_run, python


def test_no_select():
    # language=python
    rewrite_run(python("assert len('a')"))


def test_select():
    # language=python
    rewrite_run(python("assert 'a'.islower( )"))


def test_invoke_function_receiver():
    # language=python
    rewrite_run(python("assert a(0)(1)"))
