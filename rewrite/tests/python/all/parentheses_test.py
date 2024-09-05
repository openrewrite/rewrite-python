from rewrite.test import rewrite_run, python


def test_single():
    # language=python
    rewrite_run(python("assert (True)"))


def test_left():
    # language=python
    rewrite_run(python("assert (True) or False"))


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


def test_multiline():
    # language=python
    rewrite_run(
        python(
            """
            b = (
                True
            ) or False
            """
        )
    )
