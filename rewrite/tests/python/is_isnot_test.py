from rewrite.test import rewrite_run, python


def test_is():
    # language=python
    rewrite_run(
        python(
            """\
            def test(a, b):
                return a is b
            """
        )
    )


def test_isnot():
    # language=python
    rewrite_run(
        python(
            """\
            def test(a, b):
                return a is not b
            """
        )
    )
