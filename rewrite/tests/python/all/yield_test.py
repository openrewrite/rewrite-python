from rewrite.test import rewrite_run, python


def test_yield():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
                yield 1
            """
        )
    )


def test_yield_from():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
                yield from range(5)
            """
        )
    )
