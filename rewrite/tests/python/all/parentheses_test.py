import pytest

from rewrite.test import rewrite_run, python


def test_single():
    # language=python
    rewrite_run(python("assert (True)"))


def test_double():
    # language=python
    rewrite_run(python("assert ((True))"))


def test_nested_1():
    # language=python
    rewrite_run(python("assert ((True) or False)"))


def test_nested_2():
    # language=python
    rewrite_run(python("assert (True or (False))"))


def test_nested_spaces():
    # language=python
    rewrite_run(python("assert (  True or ( False ) )"))


def test_assign_parens():
    # language=python
    rewrite_run(
        python(
            """
            total_months = ( (2 - 1) * 12 + (3 + 4) 
            + 1)
            """
        )
    )
