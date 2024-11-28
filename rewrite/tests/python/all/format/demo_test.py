from typing import Optional

from rewrite.java import Space, P
from rewrite.python import PythonVisitor
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

class NoSpaces(PythonVisitor):
    def visit_space(self, space: Optional[Space], loc: Optional[Space.Location], p: P) -> Optional[Space]:
        return Space.EMPTY if space else None