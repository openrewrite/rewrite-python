from rewrite.test import rewrite_run, python


# language=python
def test_formatting():
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


# language=python
def test_with_message():
    rewrite_run(python("assert True, 'foo'"))


# language=python
def test_assert():
    rewrite_run(python("assert True"))
