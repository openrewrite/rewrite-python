from rewrite.test import rewrite_run, python


def test_while():
    # language=python
    rewrite_run(
        python(
            """\
            def test(i):
                while i < 6:
                    i += 1
            """
        )
    )


def test_while_else():
    # language=python
    rewrite_run(
        python(
            """\
            def test(i):
                while i < 6:
                    i += 1
                else:
                    i = 10
            """
        )
    )
