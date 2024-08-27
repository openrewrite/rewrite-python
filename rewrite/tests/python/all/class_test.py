from rewrite.test import rewrite_run, python


def test_empty():
    # language=python
    rewrite_run(
        python(
            """\
            class Foo:
                pass
            """
        )
    )


def test_field():
    # language=python
    rewrite_run(
        python(
            """\
            class Foo:
                _f = 0
            """
        )
    )
