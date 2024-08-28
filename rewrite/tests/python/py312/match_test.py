import pytest

from rewrite.test import rewrite_run, python


def test_simple():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case 1:
                        pass
                    case 2:
                        pass
            """
        )
    )


def test_as():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case 1 as y:
                        return y
            """
        )
    )


def test_sequence_as():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case [int(), str()] as y:
                        return y
            """
        )
    )


def test_wildcard():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case 1:
                        pass
                    case _:
                        pass
            """
        )
    )


def test_wildcard_as():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case 1:
                        pass
                    case _ as x:
                        return x
            """
        )
    )


def test_sequence():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case [1, 2]:
                        pass
            """
        )
    )


def test_nested():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case [int(), str()]:
                        pass
            """
        )
    )


def test_star():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case [1, *rest]:
                        return rest
            """
        )
    )


def test_guard():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case [1, *rest] if 42 > rest:
                        return rest
            """
        )
    )


def test_or():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case 1 | 2:
                        pass
            """
        )
    )


def test_value():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x, value):
                match x:
                    case value.pattern:
                        pass
            """
        )
    )


def test_group():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x, value):
                match x:
                    case (value.pattern):
                        pass
            """
        )
    )


def test_mapping():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case {"x": x, "y": y, **z}:
                        return x+y+z
            """
        )
    )


def test_sequence_target():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x, y):
                match x, y:
                    case a, b:
                        return a+b
            """
        )
    )


@pytest.mark.parametrize("args", ['', 'a', 'b, c', 'a, b=c', 'a, b=c, d=(e,f)'])
def test_class(args):
    rewrite_run(
        python(
            """\
            from abc import ABC
            
            def test(x, y):
                match x:
                    case ABC({0}):
                        pass
            """.format(args)
        )
    )
