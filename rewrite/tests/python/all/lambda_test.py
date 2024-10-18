from rewrite.test import rewrite_run, python


def test_no_parameters():
    # language=python
    rewrite_run(python("l = lambda: None"))


def test_single_parameter():
    # language=python
    rewrite_run(python("l = lambda x: x"))


def test_multiple_parameter():
    # language=python
    rewrite_run(python("l = lambda x, y: x + y"))


def test_parameters_with_defaults():
    # language=python
    rewrite_run(python("l = lambda x, y=0: x + y"))


def test_parameters_with_defaults_2():
    # language=python
    rewrite_run(python('l = lambda self, v, n=n: 1'))
