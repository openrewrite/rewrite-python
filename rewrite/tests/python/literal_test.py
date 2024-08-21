from rewrite.test import rewrite_run, python


# language=python
def test_none():
    rewrite_run(python("assert None"))


# language=python
def test_boolean():
    rewrite_run(python("assert True or False"))


# language=python
def test_number():
    rewrite_run(python("assert 0 or 0.0"))
