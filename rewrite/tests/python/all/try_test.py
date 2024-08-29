import pytest

from rewrite.test import rewrite_run, python


def test_try_except():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
                try:
                    pass
                except:
                    pass
            """
        )
    )


def test_try_except_finally():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
                try:
                    pass
                except NotImplementedError:
                    pass
                except OverflowError as e:
                    pass
                except:
                    pass
                finally:
                    pass
            """
        )
    )


@pytest.mark.xfail(reason="Implementation still not quite correct", strict=True)
def test_try_else():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
                try:
                    result = 1 / 1
                except ZeroDivisionError:
                    print("Caught a division by zero error!")
                else:
                    print("No error occurred, result is:", result)
            """
        )
    )
