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
