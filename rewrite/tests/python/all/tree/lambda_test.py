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


def test_positional_only():
    # language=python
    rewrite_run(python('l = lambda a, /, b: ...'))


def test_positional_only_last():
    # language=python
    rewrite_run(python('l = lambda a=1, /: ...'))


def test_positional_only_last_trailing_comma():
    # language=python
    rewrite_run(python('l = lambda a, /,: ...'))


def test_keyword_only():
    # language=python
    rewrite_run(python('l = lambda kw=1, *, a: ...'))


def test_complex():
    # language=python
    rewrite_run(python('l = lambda a, b=20, /, c=30: 1'))


def test_multiple_complex():
    # language=python
    rewrite_run(python('''\
        lambda a, b=20, /, c=30: 1
        lambda a, b, /, c, *, d, e: 0
    '''))
