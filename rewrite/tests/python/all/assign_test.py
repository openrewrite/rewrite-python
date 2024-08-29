from rewrite.test import rewrite_run, python


def test_assign():
    # language=python
    rewrite_run(python("a = 1"))


def test_assign():
    # language=python
    rewrite_run(python("(a := 1)"))


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
