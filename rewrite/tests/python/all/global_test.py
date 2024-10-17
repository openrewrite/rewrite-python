from rewrite.test import rewrite_run, python


def test_simple():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
              global x
              x = 1
            """
        )
    )

def test_multiple():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
              global x , y
              x = 1
            """
        )
    )
