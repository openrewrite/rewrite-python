from dataclasses import dataclass
from typing import Any, Callable

from rewrite.java import Literal, P, J, Expression
from rewrite.python import PythonVisitor, PythonTemplate
from rewrite.test import from_visitor, RecipeSpec, rewrite_run, python


def test_simple():
    # language=python
    rewrite_run(
        python("a = 1", "a = 2"),
        spec=RecipeSpec()
        .with_recipe(from_visitor(ExpressionTemplatingVisitor(lambda j: isinstance(j, Literal), '2')))
    )


@dataclass
class ExpressionTemplatingVisitor(PythonVisitor[Any]):
    match: Callable[[J], bool]
    code: str

    def visit_expression(self, expr: Expression, p: P) -> J:
        return PythonTemplate(self.code) \
            .apply(self.cursor, expr.get_coordinates().replace()) \
            if self.match(expr) else expr
