from rewrite.test import rewrite_run, python


def test_assign():
    # language=python
    rewrite_run(python("a = 1"))


def test_assign_2():
    # language=python
    rewrite_run(python("a.b: int = 1"))


def test_assign_no_init():
    # language=python
    rewrite_run(python("a : int"))


def test_assign_expression():
    # language=python
    rewrite_run(python("(a := 1)"))


def test_assign_in_if():
    # language=python
    rewrite_run(
        python(
            """
            if True:
                a = 1
            elif True:
                a = 2
            else:
                a = 3
            """
        )
    )


def test_assign_in_while_loop():
    # language=python
    rewrite_run(
        python(
            """\
            while True:
                a = 1
            """
        )
    )


def test_assign_in_for_loop():
    # language=python
    rewrite_run(
        python(
            """
            for i in range(10):
                a = 2
            """
        )
    )


def test_assign_in_try():
    # language=python
    rewrite_run(
        python(
            """
            try:
                a = 1
            except Exception:
                a = 2
            """
        )
    )


def test_assign_op():
    # language=python
    rewrite_run(python("a += 1"))
    # language=python
    rewrite_run(python("a -= 1"))
    # language=python
    rewrite_run(python("a *= 1"))
    # language=python
    rewrite_run(python("a /= 1"))
    # language=python
    rewrite_run(python("a %= 1"))
    # language=python
    rewrite_run(python("a |= 1"))
    # language=python
    rewrite_run(python("a &= 1"))
    # language=python
    rewrite_run(python("a ^= 1"))
    # language=python
    rewrite_run(python("a **= 1"))
    # language=python
    rewrite_run(python("a //= 1"))
    # language=python
    rewrite_run(python("a @= 1"))
