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


def test_tuple():
    # language=python
    rewrite_run(
        python(
            """
            def foo():
                return 1, 2, 3
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
