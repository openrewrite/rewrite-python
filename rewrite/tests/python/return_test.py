from rewrite.test import rewrite_run, python


def test_empty():
    # language=python
    rewrite_run(
        python(
            """
            def foo():
                return
            """
        )
    )


def test_trailing_semicolon():
    # language=python
    rewrite_run(
        python(
            """
            def foo():
                return;
            """
        )
    )


def test_value():
    # language=python
    rewrite_run(
        python(
            """
            def foo():
                return 1
            """
        )
    )
