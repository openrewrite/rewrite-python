from typing import Any

from rewrite.java import Literal, P, J
from rewrite.python import PythonVisitor, PythonTemplate, PythonParserBuilder
from rewrite.test import from_visitor, RecipeSpec, rewrite_run, python


def test_simple():
    # language=python
    rewrite_run(
        python("a = 1", "a = 2"),
        spec=RecipeSpec()
        .with_recipe(from_visitor(TemplatingVisitor()))
    )


class TemplatingVisitor(PythonVisitor[Any]):
    def visit_literal(self, literal: Literal, p: P) -> J:
        return PythonTemplate('2') \
            .apply(self.cursor, literal.get_coordinates().replace()) \
            .with_prefix(literal.prefix)
