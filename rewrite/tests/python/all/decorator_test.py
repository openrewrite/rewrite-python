from rewrite.test import rewrite_run, python


def test_function_unqualified():
    # language=python
    rewrite_run(
        python(
            """\
            from functools import lru_cache
            
            @lru_cache
            def f(n):
                return n
            """
        )
    )


def test_function_no_parens():
    # language=python
    rewrite_run(
        python(
            """\
            import functools
            
            @functools.lru_cache
            def f(n):
                return n
            """
        )
    )


def test_function_empty_parens():
    # language=python
    rewrite_run(
        python(
            """\
            import functools
            
            @functools.lru_cache(1)
            def f(n):
                return n
            """
        )
    )


def test_function_with_arg():
    # language=python
    rewrite_run(
        python(
            """\
            import functools
            
            @functools.lru_cache(1, )
            def f(n):
                return n
            """
        )
    )


def test_function_with_named_arg():
    # language=python
    rewrite_run(
        python(
            """\
            import functools
            
            @functools.lru_cache(maxsize=1)
            def f(n):
                return n
            """
        )
    )


def test_class_no_parens():
    # language=python
    rewrite_run(
        python(
            """\
            from dataclasses import dataclass
            
            @dataclass
            class T:
                pass
            """
        )
    )


def test_class_empty_parens():
    # language=python
    rewrite_run(
        python(
            """\
            import dataclasses
            
            @dataclasses.dataclass()
            class T:
                pass
            """
        )
    )
