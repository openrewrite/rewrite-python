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


def test_enum():
    # language=python
    rewrite_run(
        python(
            """\
            from enum import Enum
            class Foo(Enum):
                '''Foo'''
                Foo = 'Foo'
                '''Bar'''
                Bar = 'Bar'
            """
        )
    )


def test_single_base():
    # language=python
    rewrite_run(
        python(
            """\
            import abc
            class Foo (abc.ABC) :
                pass
            """
        )
    )


def test_two_bases():
    # language=python
    rewrite_run(
        python(
            """\
            import abc
            class Foo(abc.ABC, abc.ABC,):
                pass
            """
        )
    )


def test_empty_parens():
    # language=python
    rewrite_run(
        python(
            """\
            class Foo (  ):
                pass
            """
        )
    )
