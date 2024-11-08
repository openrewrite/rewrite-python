from rewrite.test import rewrite_run, python


# noinspection PyCompatibility
def test_type_alias():
    # language=python
    rewrite_run(
        python(
            """\
            from typing import Tuple

            type Coordinates = Tuple[float, float]
            """
        ))
