from rewrite.test import rewrite_run, python


def test_for():
    # language=python
    rewrite_run(
        python(
            """\
            for x in [1]:
                pass
            """
        )
    )


def test_for_with_destruct():
    # language=python
    rewrite_run(
        python(
            """\
            for x, y in [(1,2),(3,4)]:
                pass
            """
        )
    )


def test_for_with_destruct_and_parens_1():
    # language=python
    rewrite_run(
        python(
            """\
            for (x, y) in [(1,2),(3,4)]:
                pass
            """
        )
    )


def test_for_with_target_expression():
    # language=python
    rewrite_run(
        python(
            """\
            for d['a'] in [1, 2, 3]:
                pass
            """
        )
    )


def test_for_with_else():
    # language=python
    rewrite_run(
        python(
            """\
            for x in [1]:
                pass
            else:
                pass
            """
        )
    )


def test_async():
    # language=python
    rewrite_run(
        python(
            """\
            async for x in [1]:
                pass
            """
        )
    )
