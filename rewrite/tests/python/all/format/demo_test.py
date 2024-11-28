from typing import Optional

from rewrite import NamedStyles
from rewrite.java import Space, P
from rewrite.python import PythonVisitor, AutoFormat, PythonParserBuilder, IntelliJ
from rewrite.test import rewrite_run, python, from_visitor, RecipeSpec


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
        spec=RecipeSpec()
        .with_recipe(from_visitor(NoSpaces()))
        .with_parsers([PythonParserBuilder().styles(NamedStyles.build(IntelliJ.spaces()))])
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
        spec=RecipeSpec(_recipe=AutoFormat())
    )

class NoSpaces(PythonVisitor):
    def visit_space(self, space: Optional[Space], loc: Optional[Space.Location], p: P) -> Optional[Space]:
        return Space.EMPTY if space else None
