from rewrite.test import rewrite_run, python


def test_whitespace_before_colon():
    # language=python
    rewrite_run(
        python(
            """\
            def foo() :
                pass
            """
        )
    )


def test_varargs():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(*args) :
                pass
            """
        )
    )


def test_kwargs():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x, **kwargs) :
                pass
            """
        )
    )


# https://peps.python.org/pep-3102/
def test_keyword_only_args():
    # language=python
    rewrite_run(
        python(
            """\
            def func(x, *, kwarg1, kwarg2):
                pass
            """
        )
    )


def test_one_line():
    # language=python
    rewrite_run(python("def f(x): x = x + 1; return x"))


def test_line_break_after_last_param():
    # language=python
    rewrite_run(
        python(
            """\
            def f(
                x = 0,
            ):
                return x
            """
        )
    )
