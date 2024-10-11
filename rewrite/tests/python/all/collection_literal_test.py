from rewrite.test import rewrite_run, python


def test_empty_tuple():
    # language=python
    rewrite_run(python("t = ( )"))


def test_single_element_tuple():
    # language=python
    rewrite_run(python("t = (1 )"))


def test_single_element_tuple_with_trailing_comma():
    # language=python
    rewrite_run(python("t = (1 , )"))


def test_tuple_with_first_element_in_parens():
    # language=python
    rewrite_run(python("x = (1) // 2, 0"))


# note: `{}` is always a dict
def test_empty_set():
    # language=python
    rewrite_run(python("t = set()"))


def test_single_element_set():
    # language=python
    rewrite_run(python("t = {1 }"))


def test_single_element_set_with_trailing_comma():
    # language=python
    rewrite_run(python("t = {1 , }"))
