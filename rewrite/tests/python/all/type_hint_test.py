from rewrite.test import rewrite_run, python


def test_primitive_type_hint():
    # language=python
    rewrite_run(
        python(
            """\
            def test(n : int):
                return n + 1
            """
        )
    )


def test_return_type_type_hint():
    # language=python
    rewrite_run(
        python(
            """\
            def test(n: int)  ->  int :
                return n + 1
            """
        )
    )


def test_class_type_hint():
    # language=python
    rewrite_run(
        python(
            """\
            from typing import List

            def test(n: List):
                return n[0] + 1
            """
        )
    )


def test_generic_type_hint():
    # language=python
    rewrite_run(
        python(
            """\
            from typing import List

            def test(n: List[int]):
                return n[0] + 1
            """
        )
    )


def test_generic_type_hint_multiple_params():
    # language=python
    rewrite_run(
        python(
            """\
            from typing import Callable

            def test(n: Callable[[int], str]):
                return n(1)
            """
        )
    )


def test_generic_type_hint_literal_params():
    # language=python
    rewrite_run(
        python(
            """\
            from typing_extensions import Literal
            mode: Literal['before', 'after'] = 'before'
            """
        )
    )


def test_variable_with_type_hint():
    # language=python
    rewrite_run(python("""foo: int = 1"""))


def test_variable_with_parameterized_type_hint():
    # language=python
    rewrite_run(python("""foo: Union[None, ...] = None"""))


def test_variable_with_parameterized_type_hint_in_quotes():
    # language=python
    rewrite_run(python("""foo: Dict["Foo", str] = None"""))


def test_variable_with_quoted_type_hint():
    # language=python
    rewrite_run(python("""foo: 'Foo' = None"""))


def test_function_parameter_with_quoted_type_hint():
    # language=python
    rewrite_run(
        python(
            """\
            def foo(s: "str"):
                pass
            """
        ))

