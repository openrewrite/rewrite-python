from rewrite.test import rewrite_run, python


def test_raise():
    # language=python
    rewrite_run(
        python(
            """\
            def test(n):
                if n == 42:
                    raise ValueError("42")
                pass
            """
        )
    )
