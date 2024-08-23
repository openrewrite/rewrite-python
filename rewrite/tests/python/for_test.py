from rewrite.test import rewrite_run, python


def test_for():
    # language=python
    rewrite_run(
        python(
            """\
            for x in xs:
                pass
            """
        )
    )

def test_for_with_else():
    # language=python
    rewrite_run(
        python(
            """\
            for x in xs:
                pass
            else:
                pass
            """
        )
    )
