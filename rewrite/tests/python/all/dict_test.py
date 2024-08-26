from rewrite.test import rewrite_run, python


def test_empty():
    # language=python
    rewrite_run(python("d = { }"))


def test_single():
    # language=python
    rewrite_run(python("d = {'x' :   1 }"))


def test_multiple():
    # language=python
    rewrite_run(python("d = {'x':1 , 'y':2 }"))


def test_trailing_comma():
    # language=python
    rewrite_run(python("d = {'x':1 , }"))
