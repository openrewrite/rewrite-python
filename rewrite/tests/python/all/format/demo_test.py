from typing import Optional

from rewrite.java import Space, P
from rewrite.python import PythonVisitor, AutoFormat
from rewrite.test import rewrite_run, python, from_visitor


def test_remove_all_spaces_demo():
    rewrite_run(
        python(
            # language=python
            """
            class Foo:
                def getter(self, row):
                    pass
            """, """classFoo:defgetter(self,row):pass"""
        ),
        recipe=from_visitor(NoSpaces())
    )


def test_spaces_before_method_parentheses():
    rewrite_run(
        # language=python
        python(
            """
            class Foo:
                def getter  (self, row):
                    pass
            """,
            """
            class Foo:
                def getter(self, row):
                    pass
            """
        ),
        recipe=AutoFormat()
    )

class NoSpaces(PythonVisitor):
    def visit_space(self, space: Optional[Space], loc: Optional[Space.Location], p: P) -> Optional[Space]:
        return Space.EMPTY if space else None
