from rewrite.test import rewrite_run, python


def test_global():
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

def test_nonlocal():
    # language=python
    rewrite_run(
        python(
            """\
            def test():
              nonlocal x
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
