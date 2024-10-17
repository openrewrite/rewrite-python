import pytest

from rewrite.test import rewrite_run, python


def test_if():
    # language=python
    rewrite_run(
        python(
            """\
            if True:
                pass
            """
        )
    )


def test_else_single():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(b):
                if b:
                    pass
                else:
                    pass
            """
        )
    )


def test_if_with_tuple_1():
    # language=python
    rewrite_run(
        python(
            """\
            import sys
            if (sys.version_info[0], sys.version_info[1]) < (3, 8):
                pass
            """
        )
    )


def test_if_with_tuple_2():
    # language=python
    rewrite_run(
        python(
            """\
            import sys
            if ((sys.version_info[0], sys.version_info[1]) < (3, 8)):
                pass
            """
        )
    )


def test_else_multiple():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(b):
                if b:
                    pass
                else:
                    x = 0
                    pass
            """
        )
    )


def test_elfif_else():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(b):
                if b == 0:
                    pass
                elif b == 1 :
                    pass
                else:
                    pass
            """
        )
    )


def test_multiple_elif_else():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(b):
                if b == 0:
                    pass
                elif b == 1:
                    pass
                elif b == 2 :
                    pass
                else :
                    pass
            """
        )
    )


def test_if_nested_in_else():
    # language=python
    rewrite_run(
        python(
            """\
            if True:
                pass
            else :
                if False:
                    pass
            """
        )
    )
