from rewrite.test import rewrite_run, python


# NOTE: This was added in Python 3.10
# noinspection PyUnresolvedReferences
def test_simple():
    # language=python
    rewrite_run(python("foo: int | str = 42"))
