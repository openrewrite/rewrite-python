from rewrite.test import rewrite_run, python


def test_basic_comprehension():
    # language=python
    rewrite_run(python("a = [ e+1 for e in [1, 2, ]]"))


def test_comprehension_with_if():
    # language=python
    rewrite_run(python("a = [ e+1 for e in [1, 2, ] if e > 1]"))


def test_comprehension_with_multiple_ifs():
    # language=python
    rewrite_run(python("a = [ e+1 for e in [1, 2, ] if e > 1  if e < 10]"))
