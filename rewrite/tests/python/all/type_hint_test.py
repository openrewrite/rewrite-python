from rewrite.test import rewrite_run, python


def test_primitive_type_hint():
    # language=python
    rewrite_run(
        python(
            """\
            def test(n: int):
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
