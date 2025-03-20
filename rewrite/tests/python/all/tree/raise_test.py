from rewrite.test import rewrite_run, python


def test_raise():
    # language=python
    rewrite_run(
        python(
            """\
            if n == 42:
                raise ValueError("42")
            """
        )
    )


def test_raise_from():
    # language=python
    rewrite_run(
        python(
            """\
            try:
                1 / 0
            except ZeroDivisionError as e:
                raise ValueError("42") from e
            """
        )
    )
