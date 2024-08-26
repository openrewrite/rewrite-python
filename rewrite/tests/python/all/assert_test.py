from rewrite.test import rewrite_run, python


def test_formatting():
    # language=python
    rewrite_run(
        python(
            """\
            assert \\
            True \\
            ,\\
            'foo'
            """,
        ),
    )


def test_with_message():
    # language=python
    rewrite_run(python("assert True, 'foo'"))


def test_assert():
    # language=python
    rewrite_run(python("assert True"))
